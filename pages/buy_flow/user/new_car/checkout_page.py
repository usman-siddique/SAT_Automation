import re
from urllib.parse import parse_qs, urlparse

from playwright.sync_api import Page

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
            assert actual == expected, (
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

    def continue_to_payment(self):
        continue_button = self.page.locator("button.checkout--btn.placeOrder").first
        continue_button.wait_for(state="visible")
        assert continue_button.is_enabled(), "New Car Continue button is disabled"
        continue_button.click()
        self.page.wait_for_url("**/proceed-to-payment**")
        print("Opened New Car payment page")
        return self
