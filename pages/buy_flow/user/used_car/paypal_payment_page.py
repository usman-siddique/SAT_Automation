import re

from playwright.sync_api import TimeoutError as PlaywrightTimeoutError

from pages.buy_flow.user.payment_page import PaymentPage
from pages.buy_flow.user.used_car.snapshot import (
    UsedCarCheckoutSnapshot,
    UsedCarPayPalPrices,
)


class UsedCarPayPalPaymentPage(PaymentPage):
    """Used Car PayPal assertions across USD, JPY, and confirmation."""

    def _payment_summary_value(self, label_text: str):
        label = self.page.locator(
            "td.c-price-title", has_text=label_text
        ).first
        label.wait_for(state="visible")
        return label.locator("xpath=ancestor::tr[1]").locator(
            "td.c-price"
        ).inner_text().strip()

    @staticmethod
    def _normalize_text(value: str):
        return re.sub(r"[^a-z0-9]", "", value.lower())

    @staticmethod
    def _is_ask(value: str):
        return value.strip().lower() == "ask"

    def _assert_price(self, actual: str, expected: str, description: str):
        if self._is_ask(expected):
            assert self._is_ask(actual), (
                f"{description} should remain Ask, found {actual!r}."
            )
            return
        assert self._normalize_price(actual) == self._normalize_price(expected), (
            f"{description} changed: expected {expected}, found {actual}."
        )

    def _wait_for_converted_price(self, label: str, usd_value: str):
        converted_value = ""
        for _ in range(30):
            converted_value = self._payment_summary_value(label)
            if self._is_ask(usd_value):
                if self._is_ask(converted_value):
                    return converted_value
            elif (
                not self._is_ask(converted_value)
                and self._normalize_price(converted_value)
                != self._normalize_price(usd_value)
            ):
                return converted_value
            self.page.wait_for_timeout(1000)

        if self._is_ask(usd_value):
            raise AssertionError(
                f"{label} was Ask in USD but changed to {converted_value!r} "
                "after selecting PayPal."
            )
        raise AssertionError(
            f"PayPal changed the {label} currency display but did not convert "
            f"its numeric amount: {usd_value!r} -> {converted_value!r}."
        )

    def verify_checkout_snapshot(self, snapshot: UsedCarCheckoutSnapshot):
        """Ensure destination, method, and USD breakdown reached payment."""
        country_expression = re.escape(snapshot.country).replace(
            r"\ ", r"[-\s]"
        )
        country_pattern = re.compile(
            rf"^{country_expression}$",
            re.IGNORECASE,
        )
        self.page.get_by_text(country_pattern).filter(visible=True).first.wait_for(
            state="visible"
        )
        self.page.get_by_text(snapshot.port, exact=True).filter(
            visible=True
        ).first.wait_for(state="visible")

        shipping_label = self.page.get_by_text(
            re.compile(r"^Shipping Method:?$", re.IGNORECASE)
        ).filter(visible=True).first
        shipping_label.wait_for(state="visible")
        shipping_text = shipping_label.locator("xpath=..").inner_text()
        assert self._normalize_text(snapshot.shipping_method) in self._normalize_text(
            shipping_text
        ), (
            "Shipping Method changed between checkout and payment: expected "
            f"{snapshot.shipping_method!r}, found {shipping_text!r}."
        )

        for label, expected in (
            ("Car Price", snapshot.car_price_usd),
            ("Shipping Cost", snapshot.shipping_cost_usd),
            ("Insurance", snapshot.insurance_usd),
            ("Warranty", snapshot.warranty_usd),
            ("Total Price", snapshot.total_price_usd),
        ):
            self._assert_price(
                self._payment_summary_value(label),
                expected,
                f"Payment-page {label}",
            )

        print(
            "Used Car payment page retained checkout destination, shipping "
            "method, and USD price breakdown"
        )
        return self

    def select_paypal_and_capture_jpy(
        self,
        snapshot: UsedCarCheckoutSnapshot,
    ):
        """Select PayPal and prove each numeric amount really converts."""
        self._wait_for_payment_page()
        paypal = self.page.locator("input[name='payment'][value='paypal']")
        paypal.wait_for(state="visible")
        paypal.check()
        assert paypal.is_checked(), "PayPal was not selected"

        self.page.locator("#paypal").wait_for(state="visible", timeout=10000)
        self.page.wait_for_function(
            """() => document.body.innerText.includes('JPY') ||
                Array.from(document.querySelectorAll('input, select'))
                    .some((element) => element.value === 'JPY')""",
            timeout=30000,
        )

        prices = UsedCarPayPalPrices(
            car_price_jpy=self._wait_for_converted_price(
                "Car Price", snapshot.car_price_usd
            ),
            shipping_cost_jpy=self._wait_for_converted_price(
                "Shipping Cost", snapshot.shipping_cost_usd
            ),
            insurance_jpy=self._wait_for_converted_price(
                "Insurance", snapshot.insurance_usd
            ),
            warranty_jpy=self._wait_for_converted_price(
                "Warranty", snapshot.warranty_usd
            ),
            total_price_jpy=self._wait_for_converted_price(
                "Total Price", snapshot.total_price_usd
            ),
        )

        notice = self.page.get_by_text(
            re.compile(r"only accept payments in JPY", re.IGNORECASE)
        ).filter(visible=True).first
        notice.wait_for(state="visible")
        print(
            "Used Car PayPal conversion verified: "
            f"car {snapshot.car_price_usd} -> {prices.car_price_jpy}, "
            f"shipping {snapshot.shipping_cost_usd} -> "
            f"{prices.shipping_cost_jpy}, total {snapshot.total_price_usd} -> "
            f"{prices.total_price_jpy}"
        )
        return prices

    def submit_paypal(self):
        proceed = self.page.locator("#submitPlaceOrder")
        proceed.wait_for(state="visible")
        assert proceed.is_enabled(), "Proceed to Checkout button is disabled"
        proceed.click()

        # The Used Car flow currently redirects straight to PayPal, while some
        # deployments display the shared Place Order confirmation modal first.
        try:
            self.page.wait_for_url("**paypal.com/**", timeout=10000)
        except PlaywrightTimeoutError:
            place_order = self.page.locator(
                "button", has_text="Place Order"
            ).last
            place_order.wait_for(state="visible", timeout=10000)
            place_order.click()
            self.page.wait_for_url("**paypal.com/**", timeout=60000)

        print("Reached PayPal sandbox for Used Car")
        return self

    def _confirmation_delivery(self):
        label = self.page.locator("span.item--title").filter(
            has_text=re.compile(r"^Deliver(?:y)?\s+To:?$", re.IGNORECASE)
        ).first
        label.wait_for(state="visible")
        return label.locator(
            "xpath=ancestor::div[contains(@class, 'item--summary')][1]"
        ).locator("span").last.inner_text().strip()

    def verify_confirmation(
        self,
        snapshot: UsedCarCheckoutSnapshot,
        prices: UsedCarPayPalPrices,
    ):
        success = self.page.get_by_text(
            re.compile(r"Thank you for placing an order with SAT", re.IGNORECASE)
        ).first
        success.wait_for(state="visible", timeout=60000)

        track_order = self.page.locator("a:visible, button:visible").filter(
            has_text=re.compile(r"Track Your Order", re.IGNORECASE)
        ).first
        track_order.wait_for(state="visible")

        expected_status = (
            "Partial Payment"
            if snapshot.shipping_requires_inquiry
            else "Payment Completed"
        )
        status = self._get_summary_value("Status")
        assert status.lower() == expected_status.lower(), (
            f"Used Car PayPal status should be {expected_status!r}, "
            f"found {status!r}."
        )

        delivery = self._confirmation_delivery()
        expected_delivery = f"{snapshot.country} / {snapshot.port}"
        assert self._normalize_text(delivery) == self._normalize_text(
            expected_delivery
        ), (
            f"Delivery changed: expected {expected_delivery!r}, found "
            f"{delivery!r}."
        )

        for label, expected in (
            ("Car Price", prices.car_price_jpy),
            ("Shipping Cost", prices.shipping_cost_jpy),
            ("Insurance", prices.insurance_jpy),
            ("Warranty", prices.warranty_jpy),
        ):
            self._assert_price(
                self._get_summary_value(label), expected, f"Confirmation {label}"
            )

        final_total = self._get_summary_value("Total Price")
        if snapshot.shipping_requires_inquiry:
            assert self._is_ask(final_total), (
                "Used Car shipping is Ask, so confirmation Total Price should "
                f"be Ask; found {final_total!r}."
            )
        else:
            self._assert_price(
                final_total, prices.total_price_jpy, "Confirmation Total Price"
            )

        print(
            f"Used Car PayPal confirmation verified: {expected_status}, "
            f"{delivery}, and matching JPY price breakdown"
        )
        return self

    def open_tracking(self):
        track_order = self.page.locator("a:visible, button:visible").filter(
            has_text=re.compile(r"Track Your Order", re.IGNORECASE)
        ).first
        track_order.click()
        self.page.wait_for_url("**/tracking-order-summary/**", timeout=60000)
        print("Opened Used Car Track Your Order")
        return self
