import re
from dataclasses import replace
from pathlib import Path

import allure
from allure_commons.types import AttachmentType
from playwright.sync_api import Page
from pypdf import PdfReader

from pages.reservation.user.used_car.snapshot import (
    AskReservationSnapshot,
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
ALREADY_RESERVED_PATTERN = re.compile(
    r"(?:already\s+(?:reserved|booked)\s+(?:this\s+)?(?:car|vehicle)|"
    r"(?:car|vehicle)\s+(?:is\s+)?already\s+(?:reserved|booked))",
    re.IGNORECASE,
)
ASK_COUNTRY_PREFERENCES = (
    "Pakistan",
    "United Kingdom",
    "Australia",
    "Kenya",
)
BASIC_SERVICES = {
    "insurance": "Insurance",
    "certificate": "Certificate",
    "inspection": "Inspection",
    "warranty": "Warranty",
}
ADD_ON_SERVICES = (
    "Pre-export Inspection",
    "Insurance Service",
    "Storage Service",
    "Non-Stolen Vehicle Check",
    "Marine Insurance Service",
    "Car Carrier Service",
    "Customs Clearance Service",
)


class ReservationRequiresInquiry(Exception):
    """The selected candidate cannot be used for the numeric-price test."""


class ReservationAlreadyExists(Exception):
    """The selected car already has a reservation for the current user."""


class ReservationHasNoAskValue(Exception):
    """The configured candidate did not produce ASK on the review page."""


class ReservationPage:
    def __init__(self, page: Page):
        self.page = page

    def _wait_for_render(self):
        self.page.wait_for_load_state("domcontentloaded")
        loader = self.page.locator(".loader")
        if loader.count() > 0:
            loader.wait_for(state="hidden", timeout=30000)

    def _visible_existing_reservation_message(self):
        messages = self.page.get_by_text(ALREADY_RESERVED_PATTERN)
        for index in range(messages.count()):
            message = messages.nth(index)
            if message.is_visible():
                return message.inner_text().strip()
        return None

    def _wait_for_existing_reservation_message(self, timeout_ms=3000):
        attempts = max(1, timeout_ms // 250)
        for attempt in range(attempts):
            message = self._visible_existing_reservation_message()
            if message:
                return message
            if attempt < attempts - 1:
                self.page.wait_for_timeout(250)
        return None

    def _raise_if_already_reserved(self, timeout_ms=3000):
        message = self._wait_for_existing_reservation_message(timeout_ms)
        if message:
            raise ReservationAlreadyExists(message)

    def _wait_for_submission_outcome(self, confirmation, timeout_ms):
        attempts = max(1, timeout_ms // 250)
        for attempt in range(attempts):
            self._raise_if_already_reserved(timeout_ms=0)
            if confirmation.is_visible():
                return True
            if attempt < attempts - 1:
                self.page.wait_for_timeout(250)
        return False

    @staticmethod
    def _canonical_price_label(label: str):
        key = normalize_text(label)
        if key.startswith("totalprice"):
            return "Total Price"
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

    @staticmethod
    def _assert_same_display_value(expected: str, actual: str, label: str):
        assert normalize_text(actual) == normalize_text(expected), (
            f"{label} changed during ASK reservation: "
            f"{expected!r} -> {actual!r}."
        )

    def _stable_price_rows(self, label_selector: str):
        previous_prices = None
        stable_reads = 0
        for _ in range(20):
            prices = self._price_rows(label_selector)
            if prices and prices == previous_prices:
                stable_reads += 1
                if stable_reads >= 2:
                    return prices
            else:
                stable_reads = 0
            previous_prices = prices
            self.page.wait_for_timeout(500)
        raise AssertionError(
            f"Reservation price breakdown did not stabilize: {previous_prices}."
        )

    @staticmethod
    def _selected_option_text(select):
        return select.locator("option:checked").inner_text().strip()

    def _select_option_text(self, select, expected_text: str):
        options = select.locator("option")
        for index in range(options.count()):
            option = options.nth(index)
            text = option.inner_text().strip()
            if normalize_text(text) != normalize_text(expected_text):
                continue
            value = option.get_attribute("value")
            if value:
                select.select_option(value=value)
            else:
                select.select_option(label=text)
            return text
        return None

    def _rate_signature(self):
        signature = []
        rates = self.page.locator("input[name='d_rates']:visible")
        for index in range(rates.count()):
            rate = rates.nth(index)
            row = rate.locator("xpath=ancestor::tr[1]")
            cells = row.locator("td")
            if cells.count() < 3:
                continue
            signature.append(
                (
                    rate.get_attribute("data-port_name") or "",
                    rate.get_attribute("data-ship_type") or "",
                    rate.get_attribute("data-ship_rate") or "",
                    cells.last.inner_text().strip(),
                )
            )
        return tuple(signature)

    def _wait_for_rates_to_stabilize(self):
        previous_signature = None
        stable_reads = 0
        for _ in range(30):
            signature = self._rate_signature()
            if signature and signature == previous_signature:
                stable_reads += 1
                if stable_reads >= 2:
                    return signature
            else:
                stable_reads = 0
            previous_signature = signature
            self.page.wait_for_timeout(500)
        raise AssertionError(
            "Delivery rates did not stabilize after changing destination."
        )

    def _select_country(self, country_name: str):
        country = self.page.locator(
            "select#buynow_countries_list:visible"
        ).first
        port = self.page.locator(
            "select#buynow_shipping_ports:visible"
        ).first
        previous_country = self._selected_option_text(country)
        previous_ports = tuple(
            option.inner_text().strip() for option in port.locator("option").all()
        )
        selected = self._select_option_text(country, country_name)
        if selected is None:
            return False

        if normalize_text(previous_country) != normalize_text(country_name):
            for _ in range(30):
                current_ports = tuple(
                    option.inner_text().strip()
                    for option in port.locator("option").all()
                )
                if (
                    normalize_text(self._selected_option_text(country))
                    == normalize_text(country_name)
                    and current_ports
                    and current_ports != previous_ports
                ):
                    break
                self.page.wait_for_timeout(500)
            else:
                raise AssertionError(
                    f"Ports did not refresh for {country_name}."
                )

        self._wait_for_rates_to_stabilize()
        return True

    def _visible_rate_options(self):
        options = []
        rates = self.page.locator("input[name='d_rates']:visible")
        for index in range(rates.count()):
            rate = rates.nth(index)
            row = rate.locator("xpath=ancestor::tr[1]")
            cells = row.locator("td")
            if cells.count() < 3:
                continue
            options.append(
                {
                    "port": (rate.get_attribute("data-port_name") or "").strip(),
                    "ship_type": (
                        rate.get_attribute("data-ship_type") or ""
                    ).strip(),
                    "configured_rate": (
                        rate.get_attribute("data-ship_rate") or ""
                    ).strip(),
                    "shipping_method": cells.nth(1).inner_text().strip(),
                    "displayed_rate": cells.last.inner_text().strip(),
                }
            )
        return options

    def _select_rate_option(self, expected_option: dict):
        port = self.page.locator(
            "select#buynow_shipping_ports:visible"
        ).first
        assert self._select_option_text(port, expected_option["port"]), (
            f"Destination port {expected_option['port']!r} is unavailable."
        )
        self.page.wait_for_timeout(1000)
        self._wait_for_rates_to_stabilize()

        rates = self.page.locator("input[name='d_rates']:visible")
        for index in range(rates.count()):
            rate = rates.nth(index)
            row = rate.locator("xpath=ancestor::tr[1]")
            cells = row.locator("td")
            if cells.count() < 3:
                continue
            rate_port = (rate.get_attribute("data-port_name") or "").strip()
            ship_type = (rate.get_attribute("data-ship_type") or "").strip()
            displayed_rate = cells.last.inner_text().strip()
            if (
                normalize_text(rate_port)
                == normalize_text(expected_option["port"])
                and normalize_text(ship_type)
                == normalize_text(expected_option["ship_type"])
                and normalize_text(displayed_rate)
                == normalize_text(expected_option["displayed_rate"])
            ):
                if not rate.is_checked():
                    rate.check(force=True)
                assert rate.is_checked(), "The requested delivery rate was not selected."
                self.page.wait_for_timeout(1000)
                return {
                    **expected_option,
                    "shipping_method": cells.nth(1).inner_text().strip(),
                    "displayed_rate": displayed_rate,
                }
        raise AssertionError(
            "The verified delivery rate disappeared before it could be selected: "
            f"{expected_option}."
        )

    def _select_preferred_ask_shipping(self):
        for country_name in ASK_COUNTRY_PREFERENCES:
            if not self._select_country(country_name):
                continue
            ask_options = [
                option
                for option in self._visible_rate_options()
                if normalize_text(option["displayed_rate"]) == "ask"
                or normalize_text(option["configured_rate"]) == "ask"
            ]
            ask_options.sort(
                key=lambda option: normalize_text(option["ship_type"])
                != "container"
            )
            for option in ask_options:
                try:
                    selected_rate = self._select_rate_option(option)
                except AssertionError:
                    continue
                return country_name, selected_rate, True

        selected_rate = self.page.locator(
            "input[name='d_rates']:checked:visible"
        ).first
        if selected_rate.count() == 0:
            options = self._visible_rate_options()
            assert options, "No fallback delivery rate is available."
            fallback = self._select_rate_option(options[0])
        else:
            row = selected_rate.locator("xpath=ancestor::tr[1]")
            cells = row.locator("td")
            fallback = {
                "port": selected_rate.get_attribute("data-port_name") or "",
                "ship_type": selected_rate.get_attribute("data-ship_type") or "",
                "configured_rate": (
                    selected_rate.get_attribute("data-ship_rate") or ""
                ),
                "shipping_method": cells.nth(1).inner_text().strip(),
                "displayed_rate": cells.last.inner_text().strip(),
            }
            fallback = self._select_rate_option(fallback)

        country = self.page.locator(
            "select#buynow_countries_list:visible option:checked"
        ).first.inner_text().strip()
        return country, fallback, False

    def _enable_available_basic_services(self):
        selected = []
        unavailable = []
        for field_name, label in BASIC_SERVICES.items():
            yes = self.page.locator(
                f"input[name='{field_name}'][value='1']:visible"
            ).first
            yes.wait_for(state="visible")
            if not yes.is_enabled():
                unavailable.append(label)
                continue
            if not yes.is_checked():
                yes.click(force=True)
            assert yes.is_checked(), f"Could not select {label}."
            selected.append(label)
        return tuple(selected), tuple(unavailable)

    def _enable_all_add_ons(self):
        selected = []
        for service_name in ADD_ON_SERVICES:
            selected_in_rendered_carousel = False
            service_was_found = False
            for _ in range(3):
                checkboxes = self.page.locator(
                    "input.form-check-input[type='checkbox']:visible"
                )
                matching_indexes = []
                for index in range(checkboxes.count()):
                    checkbox = checkboxes.nth(index)
                    card = checkbox.locator("xpath=ancestor::div[1]")
                    card_text = (
                        card.inner_text().strip() if card.count() else ""
                    )
                    if service_name.lower() in card_text.lower():
                        matching_indexes.append(index)
                service_was_found = service_was_found or bool(matching_indexes)

                if any(
                    checkboxes.nth(index).is_checked()
                    for index in matching_indexes
                ):
                    selected_in_rendered_carousel = True
                    break

                for index in matching_indexes:
                    checkbox = checkboxes.nth(index)
                    if not checkbox.is_enabled():
                        continue
                    checkbox.click(force=True)
                    self.page.wait_for_timeout(750)
                    loader = self.page.locator(".loader")
                    if loader.count() > 0 and loader.first.is_visible():
                        loader.first.wait_for(state="hidden", timeout=30000)

                    refreshed = self.page.locator(
                        "input.form-check-input[type='checkbox']:visible"
                    )
                    for refreshed_index in range(refreshed.count()):
                        refreshed_checkbox = refreshed.nth(refreshed_index)
                        card = refreshed_checkbox.locator(
                            "xpath=ancestor::div[1]"
                        )
                        card_text = (
                            card.inner_text().strip() if card.count() else ""
                        )
                        if (
                            service_name.lower() in card_text.lower()
                            and refreshed_checkbox.is_checked()
                        ):
                            selected_in_rendered_carousel = True
                            break
                    if selected_in_rendered_carousel:
                        break
                if selected_in_rendered_carousel:
                    break
            assert service_was_found, (
                f"ASK checkout add-on is missing: {service_name}."
            )
            assert selected_in_rendered_carousel, (
                f"Could not select ASK checkout add-on: {service_name}."
            )
            selected.append(service_name)
        return tuple(selected)

    def capture_ask_checkout(self, stock_id: str):
        """Configure and capture an ASK-capable reservation checkout."""
        assert "/reserve-car-payment/" in self.page.url, (
            f"Unexpected reservation checkout URL: {self.page.url}"
        )
        self._wait_for_render()

        selected_country, selected_rate, shipping_is_ask = (
            self._select_preferred_ask_shipping()
        )
        selected_services, unavailable_services = (
            self._enable_available_basic_services()
        )
        selected_add_ons = self._enable_all_add_ons()
        prices = self._stable_price_rows("td.c-title")

        country = self.page.locator(
            "select#buynow_countries_list:visible"
        ).first
        port = self.page.locator(
            "select#buynow_shipping_ports:visible"
        ).first
        actual_country = self._selected_option_text(country)
        actual_port = self._selected_option_text(port)
        assert normalize_text(actual_country) == normalize_text(
            selected_country
        ), (
            f"ASK country changed: {selected_country!r} -> {actual_country!r}."
        )
        assert normalize_text(actual_port) == normalize_text(
            selected_rate["port"]
        ), (
            "The selected ASK rate does not match the destination port: "
            f"{selected_rate['port']!r} != {actual_port!r}."
        )

        required_labels = [
            "Car Price",
            "Shipping Cost",
            *selected_services,
            *selected_add_ons,
            "Total Price",
        ]
        missing_labels = [label for label in required_labels if label not in prices]
        assert not missing_labels, (
            f"ASK checkout is missing price rows {missing_labels}: {prices}."
        )
        for label in required_labels:
            assert prices[label].strip(), f"ASK checkout {label} is blank."
        normalize_price(prices["Car Price"])
        if shipping_is_ask:
            assert normalize_text(prices["Shipping Cost"]) == "ask", (
                "The verified ASK shipping rate changed in Order Summary: "
                f"{prices['Shipping Cost']!r}."
            )

        snapshot = AskReservationSnapshot(
            stock_id=stock_id,
            country=actual_country,
            port=actual_port,
            shipping_method=selected_rate["shipping_method"],
            selected_services=selected_services,
            unavailable_services=unavailable_services,
            selected_add_ons=selected_add_ons,
            checkout_breakdown=tuple(
                (label, prices[label]) for label in required_labels
            ),
        )
        print(
            "ASK checkout captured: "
            f"{stock_id.upper()}, {actual_country} / {actual_port}, "
            f"{snapshot.shipping_method}, unavailable services "
            f"{unavailable_services or 'none'}."
        )
        return snapshot

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

        self._raise_if_already_reserved()

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

    def verify_ask_review(self, snapshot: AskReservationSnapshot):
        """Verify ASK transitions and retain the final review breakdown."""
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
            "Shipping Method changed on ASK review: "
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
                f"ASK review: {displayed_services}."
            )

        review_prices = self._stable_price_rows("td.c-price-title")
        checkout_prices = dict(snapshot.checkout_breakdown)
        required_labels = list(checkout_prices)
        missing_labels = [
            label for label in required_labels if label not in review_prices
        ]
        assert not missing_labels, (
            f"ASK review is missing price rows {missing_labels}: {review_prices}."
        )

        add_on_labels = set(snapshot.selected_add_ons)
        for label in required_labels:
            checkout_value = checkout_prices[label]
            review_value = review_prices[label]
            if label in add_on_labels and normalize_text(review_value) == "ask":
                continue
            self._assert_same_display_value(
                checkout_value,
                review_value,
                label,
            )

        ask_rows = {
            label: review_prices[label]
            for label in required_labels
            if label != "Total Price"
            and normalize_text(review_prices[label]) == "ask"
        }
        if not ask_rows:
            raise ReservationHasNoAskValue(
                "Shipping and selected add-ons produced no ASK value on "
                f"review: {review_prices}."
            )

        reviewed_snapshot = replace(
            snapshot,
            review_breakdown=tuple(
                (label, review_prices[label]) for label in required_labels
            ),
        )
        print(f"ASK review verified with inquiry rows: {ask_rows}.")
        return reviewed_snapshot

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
        if not self._wait_for_submission_outcome(confirmation, timeout_ms=8000):
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
            assert self._wait_for_submission_outcome(
                confirmation,
                timeout_ms=60000,
            ), "Submit Request confirmation did not finish."

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

    def verify_ask_confirmation(self, snapshot: AskReservationSnapshot):
        """Verify an ASK reservation and its pending-invoice explanation."""
        confirmation = self.page.get_by_text(
            re.compile(r"Thank you for Reserving your car", re.IGNORECASE)
        ).first
        confirmation.wait_for(state="visible")

        payment_status = self._confirmation_value("Payment Status")
        assert normalize_text(payment_status) == "paymentpending", (
            f"Expected Payment Pending, found {payment_status!r}."
        )

        delivery = self._confirmation_value(r"Delivery\s*to")
        expected_delivery = f"{snapshot.country} / {snapshot.port}"
        assert normalize_text(delivery) == normalize_text(expected_delivery), (
            f"ASK reservation delivery changed: {expected_delivery!r} -> "
            f"{delivery!r}."
        )

        assert snapshot.review_breakdown, (
            "ASK review prices were not captured before confirmation."
        )
        for label, expected_value in snapshot.review_breakdown:
            actual_value = self._confirmation_value(label)
            if label == "Total Price":
                assert normalize_text(actual_value) == "ask", (
                    f"ASK confirmation Total Price is {actual_value!r}."
                )
                continue
            self._assert_same_display_value(
                expected_value,
                actual_value,
                label,
            )

        invoice_heading = self.page.get_by_text("Invoice", exact=True).first
        invoice_heading.wait_for(state="visible")
        sales_message = self.page.get_by_text(
            re.compile(
                r"Sales\s+team\s+will\s+contact\s+you\s+for\s+further\s+details",
                re.IGNORECASE,
            )
        ).first
        sales_message.wait_for(state="visible")

        view_reservation = self.page.get_by_role(
            "link", name=re.compile(r"View Reservation", re.IGNORECASE)
        ).first
        view_reservation.wait_for(state="visible")
        print(
            "ASK reservation confirmation verified with Payment Pending, "
            "Total Price Ask, and pending invoice guidance."
        )
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
