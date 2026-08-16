import re

from playwright.sync_api import Page

from pages.buy_flow.user.used_car.snapshot import (
    UsedCarCheckoutSnapshot,
    UsedCarPayPalPrices,
)


class UsedCarTrackingPage:
    def __init__(self, page: Page):
        self.page = page

    @staticmethod
    def _normalize_price(value: str):
        normalized = re.sub(r"[^0-9.]", "", value)
        if not normalized:
            raise AssertionError(f"Price value was not found in {value!r}.")
        return normalized

    @staticmethod
    def _normalize_text(value: str):
        return re.sub(r"[^a-z0-9]", "", value.lower())

    def _summary_rows(self):
        rows = []
        for row in self.page.locator("tr").all():
            if not row.is_visible():
                continue
            cells = row.locator("td")
            if cells.count() < 2:
                continue
            rows.append(
                (
                    cells.first.inner_text().strip(),
                    cells.last.inner_text().strip(),
                )
            )
        return rows

    def verify_paypal_order(
        self,
        snapshot: UsedCarCheckoutSnapshot,
        prices: UsedCarPayPalPrices,
    ):
        assert "/tracking-order-summary/" in self.page.url, (
            f"Unexpected tracking URL: {self.page.url}"
        )

        expected_timeline = (
            "Partial Payment Received"
            if snapshot.shipping_requires_inquiry
            else "Payment Completed"
        )
        self.page.get_by_text(
            expected_timeline, exact=True
        ).first.wait_for(state="visible")

        rows = self._summary_rows()
        expected_delivery = f"{snapshot.country} / {snapshot.port}"
        delivery_rows = [
            value
            for label, value in rows
            if re.search(r"Delivery\s*to", label, re.IGNORECASE)
        ]
        assert delivery_rows, "Tracking order summary has no Delivery To row."
        assert self._normalize_text(delivery_rows[0]) == self._normalize_text(
            expected_delivery
        ), (
            f"Tracking delivery changed: expected {expected_delivery!r}, "
            f"found {delivery_rows[0]!r}."
        )

        expected_amount = prices.total_price_jpy
        matching_amount_rows = [
            (label, value)
            for label, value in rows
            if re.search(r"Amount|Price", label, re.IGNORECASE)
            and value.strip().lower() != "ask"
            and self._normalize_price(value)
            == self._normalize_price(expected_amount)
        ]
        assert matching_amount_rows, (
            "Tracking order summary does not contain the PayPal JPY total "
            f"{expected_amount}. Rows found: {rows}."
        )

        payment_status_rows = [
            value
            for label, value in rows
            if re.search(r"Payment Status", label, re.IGNORECASE)
        ]
        if payment_status_rows:
            payment_status = payment_status_rows[0].lower()
            expected_word = (
                "partial" if snapshot.shipping_requires_inquiry else "paid"
            )
            assert expected_word in payment_status, (
                f"Tracking Payment Status should contain {expected_word!r}, "
                f"found {payment_status_rows[0]!r}."
            )
            if snapshot.shipping_requires_inquiry:
                assert "ask" in payment_status, (
                    "Tracking Payment Status should retain ASK when shipping "
                    f"requires an inquiry; found {payment_status_rows[0]!r}."
                )

        print(
            "Used Car tracking verified: payment state, JPY amount, and "
            f"delivery {expected_delivery}"
        )
        return self
