import re

from playwright.sync_api import Page, TimeoutError as PlaywrightTimeoutError

from pages.buy_flow.user.used_car.snapshot import UsedCarCheckoutSnapshot


CHECKOUT_STABILIZATION_MS = 3000


class CheckoutPage:
    def __init__(self, page: Page):
        self.page = page

    def _wait_for_page_render(self):
        self.page.wait_for_load_state("domcontentloaded")
        loader = self.page.locator(".loader")
        if loader.count() > 0:
            loader.wait_for(state="hidden", timeout=30000)

    def _summary_value(self, label_text: str):
        label = self.page.locator("td.c-title", has_text=label_text).first
        label.wait_for(state="visible")
        return label.locator("xpath=ancestor::tr[1]").locator(
            "td.c-price"
        ).inner_text().strip()

    def select_services(self, service_ids: list):
        """Select services and allow shipping/price recalculation to finish."""
        self._wait_for_page_render()

        for service_id in service_ids:
            checkbox = self.page.locator(
                f"input.form-check-input[data-id='{service_id}']"
            ).first
            checkbox.wait_for(state="visible")
            if not checkbox.is_checked():
                checkbox.check()
                print(f"Checked service {service_id}")

        # Country, port, shipping, and totals update asynchronously.
        self.page.wait_for_timeout(CHECKOUT_STABILIZATION_MS)
        print("Checkout totals stabilization wait complete")
        return self

    def select_destination_and_shipping(
        self,
        stock_id: str,
        country_name: str,
        port_name: str,
        shipping_type: str,
    ):
        """Select the destination and retain the actual priced/Ask rate."""
        self._wait_for_page_render()
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
                country.select_option(index=0)
                self.page.wait_for_timeout(500)

        # Used Car destination/rate controls are rebuilt by separate AJAX
        # responses. Let the country response settle before selecting the port,
        # otherwise a late response can reset Bristol back to the first port.
        self.page.wait_for_timeout(CHECKOUT_STABILIZATION_MS)
        for attempt in range(3):
            port.select_option(label=port_name)
            self.page.wait_for_timeout(CHECKOUT_STABILIZATION_MS)
            selected_port = port.locator("option:checked").inner_text().strip()
            if selected_port == port_name:
                break
            if attempt == 2:
                raise AssertionError(
                    f"Destination Port reset to {selected_port!r} instead of "
                    f"remaining {port_name!r}."
                )

        rate = self.page.locator(
            "input[name='d_rates']"
            f"[data-port_name='{port_name}']"
            f"[data-ship_type='{shipping_type.lower()}']:visible"
        ).first
        for attempt in range(3):
            rate.wait_for(state="visible", timeout=30000)
            if not rate.is_checked():
                rate.check()
            self.page.wait_for_timeout(CHECKOUT_STABILIZATION_MS)
            selected_port = port.locator("option:checked").inner_text().strip()
            if rate.is_checked() and selected_port == port_name:
                break
            if selected_port != port_name:
                port.select_option(label=port_name)
                self.page.wait_for_timeout(CHECKOUT_STABILIZATION_MS)
            if attempt == 2:
                raise AssertionError(
                    f"{port_name} {shipping_type} shipping rate did not remain "
                    "selected after the checkout recalculation."
                )

        assert rate.get_attribute("data-port_name") == port_name
        assert (rate.get_attribute("data-ship_type") or "").lower() == (
            shipping_type.lower()
        )

        # Require three unchanged reads after the asynchronous location and
        # delivery-rate calculations before retaining any price.
        previous_prices = None
        stable_reads = 0
        for _ in range(15):
            current_prices = (
                self._summary_value("Car Price"),
                self._summary_value("Shipping Cost"),
                self._summary_value("Insurance"),
                self._summary_value("Warranty"),
                self._summary_value("Total Payable Amount"),
            )
            stable_reads = stable_reads + 1 if current_prices == previous_prices else 0
            if stable_reads >= 3:
                break
            previous_prices = current_prices
            self.page.wait_for_timeout(1000)
        else:
            raise AssertionError(
                "Used Car checkout prices did not stabilize after selecting "
                f"{country_name} / {port_name} / {shipping_type}."
            )

        selected_country = country.locator("option:checked").inner_text().strip()
        selected_port = port.locator("option:checked").inner_text().strip()
        assert selected_country == country_name
        assert selected_port == port_name

        rate_row = rate.locator("xpath=ancestor::tr[1]")
        shipping_method = rate_row.locator("td").nth(1).inner_text().strip()
        configured_rate = (rate.get_attribute("data-ship_rate") or "").strip()
        displayed_shipping = current_prices[1]
        if configured_rate.lower() == "ask":
            assert displayed_shipping.lower() == "ask", (
                "Selected shipping rate is Ask, but checkout shows "
                f"{displayed_shipping!r}."
            )
        else:
            normalize = lambda value: re.sub(r"[^0-9.]", "", value)
            assert normalize(configured_rate) == normalize(displayed_shipping), (
                "Selected shipping rate changed in checkout summary: "
                f"{configured_rate!r} -> {displayed_shipping!r}."
            )

        snapshot = UsedCarCheckoutSnapshot(
            stock_id=stock_id,
            country=country_name,
            port=port_name,
            shipping_method=shipping_method,
            car_price_usd=current_prices[0],
            shipping_cost_usd=current_prices[1],
            insurance_usd=current_prices[2],
            warranty_usd=current_prices[3],
            total_price_usd=current_prices[4],
        )
        print(
            "Used Car checkout captured: "
            f"{country_name} / {port_name}, {shipping_method}, "
            f"car {snapshot.car_price_usd}, shipping "
            f"{snapshot.shipping_cost_usd}, total {snapshot.total_price_usd}"
        )
        return snapshot

    def click_continue(self):
        """Continue only after the checkout page and totals have stabilized."""
        continue_btn = self.page.locator("button.checkout--btn.placeOrder")
        continue_btn.wait_for(state="visible")
        assert continue_btn.is_enabled(), "Checkout Continue button is disabled"
        continue_btn.click()
        self.page.wait_for_url("**/proceed-to-payment**", timeout=60000)
        self._wait_for_page_render()
        print("Clicked Continue")
        return self
