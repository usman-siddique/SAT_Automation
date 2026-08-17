import re
from pathlib import Path

import allure
from allure_commons.types import AttachmentType
from playwright.sync_api import Page, TimeoutError as PlaywrightTimeoutError
from pypdf import PdfReader

from pages.reservation.user.used_car.snapshot import (
    ReservationCandidate,
    ReservationSnapshot,
    normalize_price,
    normalize_text,
)


RESERVATION_STABILIZATION_MS = 1000
PRICE_LABELS = {
    "carprice": "Car Price",
    "shippingcost": "Shipping Cost",
    "insurance": "Insurance",
    "certificate": "Certificate",
    "inspection": "Inspection",
    "warranty": "Warranty",
    "totalpayableamount": "Total Price",
    "totalprice": "Total Price",
}


class ReservationRequiresInquiry(Exception):
    """The selected candidate cannot be used for the numeric-price test."""


class ReservationPage:
    def __init__(self, page: Page):
        self.page = page

    def _wait_for_render(self):
        self.page.wait_for_load_state("domcontentloaded")
        loader = self.page.locator(".loader")
        if loader.count() > 0:
            loader.wait_for(state="hidden", timeout=30000)

    @staticmethod
    def _canonical_price_label(label: str):
        key = normalize_text(label)
        return PRICE_LABELS.get(key, label.strip().rstrip(":"))

    def _price_rows(self, label_selector: str):
        prices = {}
        labels = self.page.locator(label_selector)
        for index in range(labels.count()):
            label = labels.nth(index)
            if not label.is_visible():
                continue
            row = label.locator("xpath=ancestor::tr[1]")
            value = row.locator("td.c-price").first
            if value.count() == 0:
                continue
            canonical_label = self._canonical_price_label(
                label.inner_text().strip()
            )
            prices[canonical_label] = value.inner_text().strip()
        return prices

    @staticmethod
    def _assert_same_price(expected: str, actual: str, label: str):
        assert normalize_price(actual) == normalize_price(expected), (
            f"{label} changed during reservation: "
            f"{expected!r} -> {actual!r}."
        )

    def capture_priced_checkout(self, candidate: ReservationCandidate):
        """Capture a stable reservation checkout with no Ask breakdown values."""
        assert "/reserve-car-payment/" in self.page.url, (
            f"Unexpected reservation checkout URL: {self.page.url}"
        )
        self._wait_for_render()

        country = self.page.locator(
            "select#buynow_countries_list:visible"
        ).first
        port = self.page.locator(
            "select#buynow_shipping_ports:visible"
        ).first
        country.wait_for(state="visible")
        port.wait_for(state="visible")

        selected_rate = self.page.locator(
            "input[name='d_rates']:checked:visible"
        ).first
        selected_rate.wait_for(state="visible", timeout=30000)

        previous_state = None
        stable_reads = 0
        for _ in range(15):
            prices = self._price_rows("td.c-title")
            state = (
                country.locator("option:checked").inner_text().strip(),
                port.locator("option:checked").inner_text().strip(),
                selected_rate.get_attribute("data-port_name") or "",
                selected_rate.get_attribute("data-ship_type") or "",
                selected_rate.get_attribute("data-ship_rate") or "",
                tuple(prices.items()),
            )
            stable_reads = stable_reads + 1 if state == previous_state else 0
            if stable_reads >= 2:
                break
            previous_state = state
            self.page.wait_for_timeout(RESERVATION_STABILIZATION_MS)
        else:
            raise AssertionError(
                "Reservation checkout destination and prices did not stabilize."
            )

        selected_country, selected_port = state[0], state[1]
        rate_row = selected_rate.locator("xpath=ancestor::tr[1]")
        shipping_method = rate_row.locator("td").nth(1).inner_text().strip()

        assert normalize_text(selected_country) == normalize_text(
            candidate.country
        ), (
            "Automatically selected reservation country changed: "
            f"{candidate.country!r} -> {selected_country!r}."
        )
        assert normalize_text(selected_port) == normalize_text(candidate.port), (
            "Automatically selected reservation port changed: "
            f"{candidate.port!r} -> {selected_port!r}."
        )
        assert normalize_text(shipping_method) == normalize_text(
            candidate.shipping_method
        ), (
            "Automatically selected shipping method changed: "
            f"{candidate.shipping_method!r} -> {shipping_method!r}."
        )

        required_labels = [
            "Car Price",
            "Shipping Cost",
            *candidate.selected_services,
            "Total Price",
        ]
        missing_labels = [label for label in required_labels if label not in prices]
        assert not missing_labels, (
            "Reservation checkout is missing price rows: "
            f"{missing_labels}. Found: {prices}."
        )

        ask_prices = {
            label: prices[label]
            for label in required_labels
            if "ask" in prices[label].lower()
        }
        if ask_prices:
            raise ReservationRequiresInquiry(
                f"Reservation price breakdown contains Ask: {ask_prices}."
            )

        for label in required_labels:
            normalize_price(prices[label])

        self._assert_same_price(
            candidate.car_price_usd,
            prices["Car Price"],
            "Car Price",
        )
        self._assert_same_price(
            candidate.shipping_cost_usd,
            prices["Shipping Cost"],
            "Shipping Cost",
        )
        self._assert_same_price(
            candidate.total_price_usd,
            prices["Total Price"],
            "Total Price",
        )

        snapshot = ReservationSnapshot(
            stock_id=candidate.stock_id,
            country=selected_country,
            port=selected_port,
            shipping_method=shipping_method,
            selected_services=candidate.selected_services,
            price_breakdown=tuple(
                (label, prices[label]) for label in required_labels
            ),
        )
        print(
            "Reservation checkout captured with no Ask prices: "
            f"{snapshot.stock_id.upper()}, {snapshot.country} / "
            f"{snapshot.port}, {snapshot.shipping_method}, "
            f"total {snapshot.price('Total Price')}"
        )
        return snapshot

    def continue_to_review(self):
        continue_button = self.page.get_by_role(
            "button", name="Continue", exact=True
        )
        continue_button.wait_for(state="visible")
        assert continue_button.is_enabled(), "Reservation Continue is disabled."
        continue_button.click()
        self.page.wait_for_url(
            "**/proceed-to-payment?payload=**",
            timeout=60000,
            wait_until="domcontentloaded",
        )
        self._wait_for_render()
        return self

    def verify_review(self, snapshot: ReservationSnapshot):
        """Verify destination, services, shipping, and prices before submit."""
        country = self.page.locator(".destination--country .button-text").first
        port = self.page.locator(".destination--port .button-text").first
        country.wait_for(state="visible")
        port.wait_for(state="visible")
        assert normalize_text(country.inner_text()) == normalize_text(
            snapshot.country
        )
        assert normalize_text(port.inner_text()) == normalize_text(snapshot.port)

        shipping_row = self.page.locator(
            ".info-row", has_text=re.compile(r"Shipping Method", re.IGNORECASE)
        ).first
        shipping_method = shipping_row.locator(".value").inner_text().strip()
        assert normalize_text(shipping_method) == normalize_text(
            snapshot.shipping_method
        ), (
            "Shipping Method changed on Submit Request review: "
            f"{snapshot.shipping_method!r} -> {shipping_method!r}."
        )

        displayed_services = tuple(
            service.inner_text().strip()
            for service in self.page.locator(
                ".services--added .service--item"
            ).all()
            if service.is_visible()
        )
        normalized_services = [normalize_text(value) for value in displayed_services]
        for expected_service in snapshot.selected_services:
            expected_key = normalize_text(expected_service)
            assert any(
                expected_key in displayed or displayed in expected_key
                for displayed in normalized_services
            ), (
                f"Selected service {expected_service!r} is missing from the "
                f"Submit Request review: {displayed_services}."
            )

        review_prices = self._price_rows("td.c-price-title")
        for label, expected_value in snapshot.price_breakdown:
            assert label in review_prices, (
                f"Submit Request review is missing {label}: {review_prices}."
            )
            assert "ask" not in review_prices[label].lower(), (
                f"Submit Request review changed {label} to Ask."
            )
            self._assert_same_price(
                expected_value,
                review_prices[label],
                label,
            )

        print("Submit Request review matches the captured reservation.")
        return self

    def submit_request(self):
        """Submit the reviewed reservation and wait for confirmation."""
        terms = self.page.locator("#term_conditions")
        terms.wait_for(state="visible")
        if not terms.is_checked():
            terms.check()

        submit = self.page.locator("#submitPlaceOrder")
        submit.wait_for(state="visible")
        assert submit.is_enabled(), "Submit Request is disabled."
        submit.click()

        confirmation = self.page.get_by_text(
            re.compile(r"Thank you for Reserving your car", re.IGNORECASE)
        ).first
        try:
            confirmation.wait_for(state="visible", timeout=8000)
        except PlaywrightTimeoutError:
            modal_buttons = self.page.get_by_role(
                "button",
                name=re.compile(r"Reserve|Confirm|Submit Request", re.IGNORECASE),
            )
            clicked_confirmation = False
            for index in range(modal_buttons.count() - 1, -1, -1):
                button = modal_buttons.nth(index)
                if button.is_visible() and button.get_attribute("id") != (
                    "submitPlaceOrder"
                ):
                    button.click()
                    clicked_confirmation = True
                    break
            assert clicked_confirmation, (
                "Submit Request did not reach confirmation or display a "
                "confirmation action."
            )
            confirmation.wait_for(state="visible", timeout=60000)

        print("Reservation request submitted.")
        return self

    def _confirmation_value(self, label_text: str):
        label = self.page.locator(
            "span.item--title", has_text=re.compile(label_text, re.IGNORECASE)
        ).first
        label.wait_for(state="visible")
        row = label.locator(
            "xpath=ancestor::div[contains(@class, 'item--summary')][1]"
        )
        return row.locator("span").last.inner_text().strip()

    def verify_confirmation(self, snapshot: ReservationSnapshot):
        """Verify the successful priced-reservation confirmation page."""
        confirmation = self.page.get_by_text(
            re.compile(r"Thank you for Reserving your car", re.IGNORECASE)
        ).first
        confirmation.wait_for(state="visible")

        payment_status = self._confirmation_value("Payment Status")
        assert payment_status.lower() == "payment pending", (
            f"Expected Payment Pending, found {payment_status!r}."
        )

        delivery = self._confirmation_value(r"Delivery\s*to")
        expected_delivery = f"{snapshot.country} / {snapshot.port}"
        assert normalize_text(delivery) == normalize_text(expected_delivery), (
            f"Reservation delivery changed: {expected_delivery!r} -> "
            f"{delivery!r}."
        )

        for label, expected_value in snapshot.price_breakdown:
            actual_value = self._confirmation_value(label)
            assert "ask" not in actual_value.lower(), (
                f"Confirmation changed {label} to Ask."
            )
            self._assert_same_price(expected_value, actual_value, label)

        invoice = self.page.get_by_role(
            "link", name=re.compile(r"Invoice", re.IGNORECASE)
        ).first
        invoice.wait_for(state="visible")
        invoice_href = invoice.get_attribute("href") or ""
        assert "/dashboard/download-resrve-invoice/" in invoice_href, (
            f"Unexpected reservation invoice URL: {invoice_href!r}."
        )

        view_reservation = self.page.get_by_role(
            "link", name=re.compile(r"View Reservation", re.IGNORECASE)
        ).first
        view_reservation.wait_for(state="visible")
        print("Reservation confirmation values and actions verified.")
        return self

    @staticmethod
    def _verify_invoice_text(
        invoice_text: str,
        snapshot: ReservationSnapshot,
    ):
        compact_invoice = normalize_text(invoice_text)
        for label, expected_value in snapshot.price_breakdown:
            value_key = normalize_price(expected_value)
            if label == "Car Price":
                stock_and_price = normalize_text(snapshot.stock_id) + value_key
                assert stock_and_price in compact_invoice, (
                    "Invoice does not place the expected vehicle price "
                    f"{expected_value!r} with {snapshot.stock_id.upper()}."
                )
                continue

            label_aliases = {normalize_text(label)}
            if label == "Shipping Cost":
                label_aliases.add("shippingcharges")
            elif label == "Total Price":
                label_aliases.update({"totalamount", "totalpayableamount"})

            assert any(
                f"{alias}{value_key}" in compact_invoice
                for alias in label_aliases
            ), (
                f"Invoice does not contain the expected {label} value "
                f"{expected_value!r}."
            )

    def download_and_verify_invoice(
        self,
        snapshot: ReservationSnapshot,
        download_dir: Path,
    ):
        """Download the reservation PDF and verify its complete price breakdown."""
        invoice = self.page.get_by_role(
            "link", name=re.compile(r"Invoice", re.IGNORECASE)
        ).first
        with self.page.expect_download(timeout=60000) as download_info:
            invoice.click()
        download = download_info.value
        invoice_path = download_dir / download.suggested_filename
        download.save_as(invoice_path)

        assert invoice_path.exists(), "Reservation invoice was not downloaded."
        assert invoice_path.stat().st_size > 0, "Reservation invoice is empty."

        reader = PdfReader(str(invoice_path))
        assert len(reader.pages) > 0, "Reservation invoice has no PDF pages."
        invoice_text = "\n".join(
            page.extract_text() or "" for page in reader.pages
        ).strip()
        assert invoice_text, "Reservation invoice contains no extractable text."

        allure.attach.file(
            str(invoice_path),
            name="Reservation invoice",
            attachment_type=AttachmentType.PDF,
        )
        allure.attach(
            invoice_text,
            name="Reservation invoice extracted text",
            attachment_type=AttachmentType.TEXT,
        )

        self._verify_invoice_text(invoice_text, snapshot)

        print(f"Reservation invoice verified: {invoice_path.name}")
        return invoice_path

    def open_view_reservation(self):
        view_reservation = self.page.get_by_role(
            "link", name=re.compile(r"View Reservation", re.IGNORECASE)
        ).first
        view_reservation.click()
        self.page.wait_for_url(
            "**/dashboard/my-booking**",
            timeout=60000,
            wait_until="domcontentloaded",
        )
        self._wait_for_render()
        return self
