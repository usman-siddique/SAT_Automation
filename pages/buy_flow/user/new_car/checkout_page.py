import re
from urllib.parse import parse_qs, urlparse

from playwright.sync_api import Page, TimeoutError as PlaywrightTimeoutError

from pages.buy_flow.user.new_car.variant import NewCarVariant


class NewCarCheckoutPage:
    def __init__(self, page: Page):
        self.page = page

    @staticmethod
    def _normalize_price(price_text: str):
        normalized = re.sub(r"[^0-9.]", "", price_text)
        if not normalized:
            raise AssertionError(f"Price value was not found in: {price_text!r}")
        return normalized

    def _summary_price(self, label_text: str):
        label = self.page.locator("td.c-title", has_text=label_text).first
        label.wait_for(state="visible")
        return label.locator("xpath=ancestor::tr[1]").locator(
            "td.c-price"
        ).inner_text().strip()

    def _summary_feature(self, label_text: str):
        row = self.page.locator(".specs-item-new").filter(
            has=self.page.get_by_text(label_text, exact=True)
        ).first
        row.wait_for(state="visible")
        return row.locator(".spec").inner_text().strip()

    def verify_variant_and_prices(self, variant: NewCarVariant):
        self.page.wait_for_load_state("domcontentloaded")
        assert "/new-car-checkout/" in self.page.url, (
            f"Unexpected New Car checkout URL: {self.page.url}"
        )

        query = parse_qs(urlparse(self.page.url).query)
        for option in ("color", "transmission", "drivetrain", "fuel", "seats"):
            assert query.get(option), (
                f"New Car checkout URL is missing selected {option}: {self.page.url}"
            )

        self.page.get_by_text(variant.model, exact=True).first.wait_for(
            state="visible"
        )
        for label, expected in variant.features().items():
            actual = self._summary_feature(label)
            assert actual.casefold() == expected.casefold(), (
                f"New Car checkout {label} changed: expected {expected!r}, "
                f"found {actual!r}."
            )

        checkout_car_price = self._summary_price("Car Price")
        assert self._normalize_price(checkout_car_price) == self._normalize_price(
            variant.car_price
        ), (
            "New Car price changed between details and checkout: "
            f"{variant.car_price} -> {checkout_car_price}."
        )

        checkout_total = self._summary_price("Total Price")
        self._normalize_price(checkout_total)
        print(
            f"New Car checkout verified: car {checkout_car_price}, "
            f"total {checkout_total}"
        )
        return checkout_total

    def select_destination(self, country_name: str, port_name: str):
        """Select a country and explicitly select its asynchronously loaded port."""
        country = self.page.locator(
            "select#buynow_countries_list:visible"
        ).first
        port = self.page.locator(
            "select#buynow_shipping_ports:visible"
        ).first
        country.wait_for(state="visible")
        port.wait_for(state="visible")

        port_option = port.locator("option").filter(
            has_text=re.compile(rf"^{re.escape(port_name)}$", re.IGNORECASE)
        )
        for attempt in range(2):
            country.select_option(label=country_name)
            try:
                port_option.wait_for(state="attached", timeout=30000)
                break
            except PlaywrightTimeoutError:
                if attempt == 1:
                    raise AssertionError(
                        f"{port_name} did not load for {country_name}."
                    )
                # Trigger the application's country-change request again when
                # the first asynchronous port fetch does not complete.
                country.select_option(index=0)
                self.page.wait_for_timeout(500)

        port.select_option(label=port_name)
        assert country.locator("option:checked").inner_text().strip() == country_name
        assert port.locator("option:checked").inner_text().strip() == port_name

        # The summary recalculates after both location controls settle.
        previous_prices = None
        stable_reads = 0
        for _ in range(10):
            current_prices = (
                self._summary_price("Car Price"),
                self._summary_price("Total Price"),
            )
            stable_reads = stable_reads + 1 if current_prices == previous_prices else 0
            if stable_reads >= 2:
                break
            previous_prices = current_prices
            self.page.wait_for_timeout(1000)
        else:
            raise AssertionError(
                "New Car checkout prices did not stabilize after selecting "
                f"{country_name} / {port_name}."
            )

        print(f"Selected New Car destination: {country_name} / {port_name}")
        return self

    def continue_to_payment(self):
        continue_button = self.page.locator("button.checkout--btn.placeOrder").first
        continue_button.wait_for(state="visible")
        assert continue_button.is_enabled(), "New Car Continue button is disabled"
        continue_button.click()
        self.page.wait_for_url("**/proceed-to-payment**")
        print("Opened New Car payment page")
        return self
