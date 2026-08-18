from playwright.sync_api import Page, TimeoutError as PlaywrightTimeoutError

from pages.buy_flow.user.used_car.inventory_page import UsedCarsPage
from pages.reservation.user.used_car.snapshot import (
    ReservationCandidate,
    normalize_price,
)


DETAIL_STABILIZATION_MS = 3000
SERVICE_LABELS = {
    "insurance": "Insurance",
    "certificate": "Certificate",
    "inspection": "Inspection",
    "warranty": "Warranty",
}


class ReservationDetailsPage:
    def __init__(self, page: Page):
        self.page = page

    def _wait_for_details(self):
        self.page.wait_for_load_state("domcontentloaded")
        loader = self.page.locator(".loader")
        if loader.count() > 0:
            loader.wait_for(state="hidden", timeout=30000)

    def _selected_destination(self, label: str):
        control = self.page.locator("button.satSelectBtn").filter(
            has_text=label
        ).first
        control.wait_for(state="visible")
        value = control.locator("span.button-text").inner_text().strip()
        assert value, f"The automatically selected {label} is blank."
        return value

    def _detail_price(self, label: str):
        price_label = self.page.locator(
            ".dealer-prices-search .car-price", has_text=label
        ).first
        price_label.wait_for(state="visible")
        value = price_label.locator(".price-pr").inner_text().strip()
        normalize_price(value)
        return value

    def _selected_services(self):
        selected = []
        for field_name, label in SERVICE_LABELS.items():
            yes_option = self.page.locator(
                f"input[name='{field_name}'][value='1']:checked"
            )
            if yes_option.count() > 0:
                selected.append(label)
        return tuple(selected)

    def _open_next_reservable_detail(
        self,
        inventory_url: str,
        excluded_stock_ids: set[str],
    ):
        """Open the next detail page that has a usable Reserve action."""
        used_cars = UsedCarsPage(self.page)

        while True:
            used_cars.open(inventory_url)
            stock_id = used_cars.select_any_available_used_car(
                excluded_stock_ids=excluded_stock_ids,
            )
            stock_key = stock_id.lower()
            self._wait_for_details()

            reserve = self.page.locator("a.reserve--now:visible").first
            if reserve.count() == 0:
                print(
                    "Skipping Used car without an available Reserve action: "
                    f"{stock_id.upper()}"
                )
                excluded_stock_ids.add(stock_key)
                continue

            reserve_href = (reserve.get_attribute("href") or "").lower()
            if (
                "/reserve-car-payment/" not in reserve_href
                or stock_key not in reserve_href
            ):
                print(
                    "Skipping Used car with an unexpected Reserve target: "
                    f"{stock_id.upper()} -> {reserve_href}"
                )
                excluded_stock_ids.add(stock_key)
                continue

            rates = self.page.locator("input[name='d_rates']:visible")
            try:
                rates.first.wait_for(state="visible", timeout=30000)
            except PlaywrightTimeoutError:
                print(
                    "Skipping Used car whose delivery rates did not load: "
                    f"{stock_id.upper()}"
                )
                excluded_stock_ids.add(stock_key)
                continue

            self.page.wait_for_timeout(DETAIL_STABILIZATION_MS)
            selected_rate = self.page.locator(
                "input[name='d_rates']:checked:visible"
            ).first
            if selected_rate.count() == 0:
                print(
                    "Skipping Used car without an automatically selected "
                    f"delivery rate: {stock_id.upper()}"
                )
                excluded_stock_ids.add(stock_key)
                continue

            return stock_id, reserve, selected_rate

    def open_next_priced_reservation(
        self,
        inventory_url: str,
        excluded_stock_ids: set[str],
    ):
        """Skip stale/Ask candidates and open the next priced Reserve form."""
        while True:
            stock_id, reserve, selected_rate = (
                self._open_next_reservable_detail(
                    inventory_url,
                    excluded_stock_ids,
                )
            )
            stock_key = stock_id.lower()

            rate_row = selected_rate.locator("xpath=ancestor::tr[1]")
            shipping_method = rate_row.locator("td").nth(1).inner_text().strip()
            shipping_cost = rate_row.locator("td").last.inner_text().strip()
            configured_rate = (
                selected_rate.get_attribute("data-ship_rate") or shipping_cost
            ).strip()
            if "ask" in configured_rate.lower() or "ask" in shipping_cost.lower():
                print(
                    "Skipping Used car because its automatically selected "
                    f"shipping rate is Ask: {stock_id.upper()}"
                )
                excluded_stock_ids.add(stock_key)
                continue

            car_price = self._detail_price("Car Price (USD)")
            total_price = self.page.locator(
                "#total_price_detail:visible"
            ).inner_text().strip()
            normalize_price(shipping_cost)
            normalize_price(total_price)

            country = self._selected_destination("Destination Country")
            port = self._selected_destination("Destination Port")
            rate_port = selected_rate.get_attribute("data-port_name") or ""
            assert rate_port.lower() == port.lower(), (
                "The selected delivery rate does not belong to the automatic "
                f"port: {rate_port!r} != {port!r}."
            )

            candidate = ReservationCandidate(
                stock_id=stock_id,
                country=country,
                port=port,
                shipping_method=shipping_method,
                selected_services=self._selected_services(),
                car_price_usd=car_price,
                shipping_cost_usd=shipping_cost,
                total_price_usd=total_price,
            )

            reserve.click()
            self.page.wait_for_url(
                f"**/reserve-car-payment/**/{stock_id}**",
                timeout=60000,
                wait_until="domcontentloaded",
            )
            print(
                "Opened priced reservation for "
                f"{stock_id.upper()}: {country} / {port}, {shipping_method}, "
                f"total {total_price}"
            )
            return candidate

    def open_next_reservation_checkout(
        self,
        inventory_url: str,
        excluded_stock_ids: set[str],
    ):
        """Open the next usable reservation form without filtering its price."""
        stock_id, reserve, _ = self._open_next_reservable_detail(
            inventory_url,
            excluded_stock_ids,
        )
        reserve.click()
        self.page.wait_for_url(
            f"**/reserve-car-payment/**/{stock_id}**",
            timeout=60000,
            wait_until="domcontentloaded",
        )
        print(f"Opened reservation checkout for {stock_id.upper()}.")
        return stock_id
