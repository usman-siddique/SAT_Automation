import re

from playwright.sync_api import Page

from pages.reservation.user.used_car.snapshot import (
    ReservationSnapshot,
    normalize_price,
)


class BookingPage:
    def __init__(self, page: Page):
        self.page = page

    def _booking_container(self, stock_id: str):
        stock = self.page.get_by_text(
            re.compile(re.escape(stock_id), re.IGNORECASE)
        ).first
        # The desktop booking card keeps its stock ID in a hidden responsive
        # element. Its reservation data-id is shared with the visible desktop
        # actions, which provides a stable cross-layout identity.
        stock.wait_for(state="attached", timeout=30000)
        mobile_card = stock.locator(
            "xpath=ancestor::div[contains(@class, 'row')][1]"
        )
        reservation_id = mobile_card.locator(".goToCheckout").get_attribute(
            "data-id"
        )
        assert reservation_id, (
            f"Reservation ID is missing for {stock_id.upper()}."
        )

        checkout = self.page.locator(
            f".goToCheckout[data-id='{reservation_id}']:visible"
        ).first
        checkout.wait_for(state="visible")
        container = checkout.locator(
            "xpath=ancestor::*[.//a[contains(@href, "
            f"'download-resrve-invoice/{reservation_id}')]][1]"
        )
        assert container.count() > 0 and container.is_visible(), (
            "Could not map the responsive stock record to its visible My "
            f"Booking card: {stock_id.upper()} / reservation {reservation_id}."
        )
        return container

    def verify_priced_reservation(self, snapshot: ReservationSnapshot):
        """Verify the matching priced reservation and its pending actions."""
        assert "/dashboard/my-booking" in self.page.url, (
            f"Unexpected My Booking URL: {self.page.url}"
        )
        container = self._booking_container(snapshot.stock_id)
        booking_text = container.inner_text().strip()

        expected_total = snapshot.price("Total Price")
        assert normalize_price(expected_total) in re.sub(
            r"[^0-9.]", "", booking_text
        ), (
            f"My Booking does not contain Total Price {expected_total!r}."
        )

        booking_date = re.search(
            r"\b\d{1,4}[-/]\d{1,2}[-/]\d{1,4}\b",
            booking_text,
        )
        assert booking_date, (
            f"Booking Date is not populated in the matching card: "
            f"{booking_text!r}."
        )

        self.page.get_by_text(
            "Payment Status", exact=True
        ).first.wait_for(state="visible")

        reservation_id = container.locator(
            ".goToCheckout:visible"
        ).get_attribute("data-id")
        timer = self.page.locator(
            f"[id$='timerDisplay_{reservation_id}']:visible"
        ).first
        timer.wait_for(state="visible")
        time_left = timer.inner_text().strip()
        time_left_match = re.search(r"(\d{1,2})h:", time_left, re.IGNORECASE)
        assert time_left_match, (
            f"The 12-hour Time Left countdown is missing: {time_left!r}."
        )
        remaining_hours = int(time_left_match.group(1))
        assert 0 <= remaining_hours <= 12, (
            f"Unexpected reservation countdown hour: {remaining_hours}."
        )

        self.page.get_by_text("Invoice", exact=True).first.wait_for(
            state="visible"
        )
        invoice = container.locator("a, button").filter(
            has_text=re.compile(r"Download", re.IGNORECASE)
        ).first
        invoice.wait_for(state="visible")

        checkout = container.get_by_role(
            "link", name=re.compile(r"Go to Checkout", re.IGNORECASE)
        ).first
        if checkout.count() == 0:
            checkout = container.get_by_role(
                "button", name=re.compile(r"Go to Checkout", re.IGNORECASE)
            ).first
        checkout.wait_for(state="visible")
        assert checkout.is_enabled(), "Go to Checkout is disabled."

        payment_proof = self.page.locator(
            f"[data-reserveid='{reservation_id}']:visible"
        ).filter(
            has_text=re.compile(r"Add Payment Proof", re.IGNORECASE)
        ).first
        payment_proof.wait_for(state="visible")
        assert payment_proof.is_enabled(), "Add Payment Proof is disabled."

        print(
            "My Booking verified: total, booking date, Payment Status column, "
            "12-hour countdown, invoice, checkout, and payment proof actions."
        )
        return self
