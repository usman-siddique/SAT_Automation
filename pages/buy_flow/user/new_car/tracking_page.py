import re

from playwright.sync_api import Page

from pages.buy_flow.user.new_car.variant import (
    NewCarPayPalPrices,
    NewCarVariant,
)


class NewCarTrackingPage:
    def __init__(self, page: Page):
        self.page = page

    @staticmethod
    def _normalize_price(price_text: str):
        normalized = re.sub(r"[^0-9.]", "", price_text)
        if not normalized:
            raise AssertionError(f"Price value was not found in: {price_text!r}")
        return normalized

    @staticmethod
    def _normalize_location(value: str):
        return re.sub(r"[^a-z0-9]", "", value.lower())

    def _assert_feature(self, label_text: str, expected_value: str):
        label = self.page.get_by_text(label_text, exact=True).last
        label.wait_for(state="visible")
        feature_text = label.locator("xpath=..").inner_text()
        assert expected_value.lower() in feature_text.lower(), (
            f"Tracking {label_text} changed: expected {expected_value!r}, "
            f"found {feature_text!r}."
        )

    def verify_paypal_order(
        self,
        variant: NewCarVariant,
        prices: NewCarPayPalPrices,
        country_name: str,
        port_name: str,
    ):
        assert "/tracking-order-summary/" in self.page.url, (
            f"Unexpected tracking URL: {self.page.url}"
        )
        self.page.get_by_text(
            "Partial Payment Received", exact=True
        ).first.wait_for(state="visible")
        self.page.get_by_text(variant.model, exact=True).last.wait_for(
            state="visible"
        )

        for label, expected in variant.features().items():
            self._assert_feature(label, expected)

        amount_label = self.page.locator("td.c-title").filter(
            has_text=re.compile(r"Partial Amount", re.IGNORECASE)
        ).filter(
            has_text=re.compile(
                rf"CIF to {re.escape(port_name)}", re.IGNORECASE
            )
        ).first
        amount_label.wait_for(state="visible")
        amount_value = amount_label.locator("xpath=ancestor::tr[1]").locator(
            "td"
        ).last.inner_text().strip()
        assert self._normalize_price(amount_value) == self._normalize_price(
            prices.total_price_jpy
        ), (
            "Tracking partial amount changed: expected "
            f"{prices.total_price_jpy}, found {amount_value!r}."
        )

        delivery_label = self.page.locator("td.c-title").filter(
            has_text=re.compile(r"Delivery\s+to", re.IGNORECASE)
        ).first
        delivery_label.wait_for(state="visible")
        delivery_value = delivery_label.locator("xpath=ancestor::tr[1]").locator(
            "td"
        ).last.inner_text().strip()
        expected_delivery = f"{country_name} / {port_name}"
        assert self._normalize_location(delivery_value) == self._normalize_location(
            expected_delivery
        ), (
            "Tracking delivery changed: expected "
            f"{expected_delivery!r}, found {delivery_value!r}."
        )

        print(
            "Tracked PayPal New Car order verified: matching JPY partial "
            f"amount, {expected_delivery}, and selected vehicle specifications"
        )
        return self
