import re

from playwright.sync_api import Page


PAYMENT_STABILIZATION_MS = 3000


class PaymentPage:
    def __init__(self, page: Page):
        self.page = page

    def _wait_for_payment_page(self):
        self.page.wait_for_load_state("domcontentloaded")
        loader = self.page.locator(".loader")
        if loader.count() > 0:
            loader.wait_for(state="hidden", timeout=30000)

    def select_credit_card(self):
        self._wait_for_payment_page()

        credit_card = self.page.locator("input[name='payment'][value='paygent']")
        credit_card.wait_for(state="visible")
        credit_card.check()
        self.page.locator("#paygentBlock").wait_for(state="visible", timeout=10000)
        # Allow payment details and the final displayed total to render fully.
        self.page.wait_for_timeout(PAYMENT_STABILIZATION_MS)
        print("Selected credit card payment")
        return self

    def select_bank_transfer(self):
        """Select Bank Transfer and wait for the total to stabilize."""
        self._wait_for_payment_page()
        bank_transfer = self.page.get_by_role(
            "radio", name=re.compile(r"Bank\s*Transfer", re.IGNORECASE)
        ).first
        bank_transfer.wait_for(state="visible")
        bank_transfer.check()
        assert bank_transfer.is_checked(), "Bank Transfer was not selected"
        self.page.wait_for_timeout(PAYMENT_STABILIZATION_MS)
        print("Selected Bank Transfer payment")
        return self

    def fill_card_details(self, card_number: str, expiry: str, cvc: str):
        card_input = self.page.locator("#card_number")
        card_input.wait_for(state="visible")
        card_input.fill(card_number)
        self.page.locator("#expire_date").fill(expiry)
        self.page.locator("#cvc").fill(cvc)
        print("Card details filled")
        return self

    def accept_terms(self):
        terms = self.page.locator("#term_conditions")
        terms.wait_for(state="visible")
        if not terms.is_checked():
            terms.check()
        print("Accepted terms")
        return self

    @staticmethod
    def _normalize_price(price_text: str):
        """Normalize values such as '$2,351' for reliable comparisons."""
        normalized = re.sub(r"[^0-9.]", "", price_text)
        if not normalized:
            raise AssertionError(f"Price value was not found in: {price_text!r}")
        return normalized

    def get_selected_payment_total(self):
        """Read Total Price and whether shipping still requires an inquiry."""
        total_label = self.page.locator(
            "td.c-price-title", has_text="Total Price"
        ).first
        total_label.wait_for(state="visible")
        total_row = total_label.locator("xpath=ancestor::tr[1]")
        total_text = total_row.locator("td.c-price").inner_text().strip()
        self._normalize_price(total_text)
        requires_inquiry = "inquire" in total_label.inner_text().lower()
        print(f"Payment screen total: {total_text}")
        return total_text, requires_inquiry

    def submit(self):
        """Place the order and wait for the order summary URL."""
        proceed = self.page.locator("#submitPlaceOrder")
        proceed.wait_for(state="visible")
        proceed.click()
        print("Clicked Proceed to Checkout")

        place_order_btn = self.page.locator("button:has-text('Place Order')")
        place_order_btn.wait_for(state="visible", timeout=10000)
        place_order_btn.click()
        print("Clicked Place Order in popup")

        self.page.wait_for_url("**/order-summary/**", timeout=60000)
        print("Reached order summary page")
        return self

    def submit_bank_transfer(self):
        """Reserve the car using Bank Transfer and wait for confirmation."""
        proceed = self.page.locator("#submitPlaceOrder")
        proceed.wait_for(state="visible")
        assert proceed.is_enabled(), "Proceed to Checkout button is disabled"
        proceed.click()
        print("Clicked Proceed to Checkout for Bank Transfer")

        place_order_btn = self.page.get_by_role(
            "button", name=re.compile(r"Place Order|Reserve", re.IGNORECASE)
        ).last
        place_order_btn.wait_for(state="visible", timeout=10000)
        place_order_btn.click()
        print("Confirmed Bank Transfer reservation")

        reservation_message = self.page.get_by_text(
            re.compile(r"Thank you for Reserving your car with SAT", re.IGNORECASE)
        ).first
        reservation_message.wait_for(state="visible", timeout=60000)
        print("Reached Bank Transfer reservation confirmation")
        return self

    def _get_summary_value(self, label_text: str):
        label = self.page.locator(
            "span.item--title", has_text=label_text
        ).first
        label.wait_for(state="visible")
        row = label.locator(
            "xpath=ancestor::div[contains(@class, 'item--summary')][1]"
        )
        # Payment Status uses a status-styled span while price rows use
        # span.item--value. The last span consistently contains the row value.
        return row.locator("span").last.inner_text().strip()

    def verify_order_confirmation(
        self,
        expected_total: str,
        payment_total_requires_inquiry: bool,
    ):
        """Verify success controls and the unchanged Total Price."""
        success_message = self.page.locator(
            "p.para", has_text="Thank you for placing an order with SAT"
        ).first
        success_message.wait_for(state="visible")

        track_btn = self.page.get_by_role("button", name="Track Your Order")
        track_btn.wait_for(state="visible")

        summary_total = self._get_summary_value("Total Price")
        if summary_total.lower() == "ask":
            shipping_cost = self._get_summary_value("Shipping Cost")
            assert shipping_cost.lower() == "ask", (
                "Order summary Total Price is Ask, but Shipping Cost is "
                f"{shipping_cost!r}."
            )
            assert payment_total_requires_inquiry, (
                "Order summary Total Price is Ask, but the Paygent screen did "
                "not indicate that the final total requires an inquiry."
            )
            print(
                f"Order confirmation verified: Paygent showed known total "
                f"{expected_total}; final total is Ask because shipping is Ask."
            )
        else:
            assert self._normalize_price(summary_total) == self._normalize_price(
                expected_total
            ), (
                f"Total Price changed after order placement: payment screen "
                f"showed {expected_total}, order summary showed {summary_total}."
            )
            print(
                f"Order confirmation verified with matching total: {summary_total}"
            )
        return self

    def verify_bank_reservation(
        self,
        expected_total: str,
        payment_total_requires_inquiry: bool,
    ):
        """Verify Bank Transfer reservation behavior for priced and Ask cases."""
        reservation_message = self.page.get_by_text(
            re.compile(r"Thank you for Reserving your car with SAT", re.IGNORECASE)
        ).first
        reservation_message.wait_for(state="visible")

        view_reservation = self.page.get_by_role(
            "link", name=re.compile(r"View Reservation", re.IGNORECASE)
        ).first
        view_reservation.wait_for(state="visible")

        payment_status = self._get_summary_value("Payment Status")
        assert payment_status.lower() == "payment pending", (
            "Bank Transfer reservation should have Payment Pending status, "
            f"but found {payment_status!r}."
        )

        shipping_cost = self._get_summary_value("Shipping Cost")
        summary_total = self._get_summary_value("Total Price")
        shipping_is_ask = shipping_cost.lower() == "ask"

        if shipping_is_ask:
            assert summary_total.lower() == "ask", (
                "Shipping Cost is Ask, so the reservation Total Price should "
                f"also be Ask; found {summary_total!r}."
            )
            assert payment_total_requires_inquiry, (
                "Confirmation shows Ask shipping, but the payment screen did "
                "not indicate that the final total requires an inquiry."
            )

            sales_message = self.page.get_by_text(
                re.compile(
                    r"Sales team will contact you for further details",
                    re.IGNORECASE,
                )
            ).first
            sales_message.wait_for(state="visible")

            invoice_link = self.page.get_by_role(
                "link", name=re.compile(r"Download Performa Invoice", re.IGNORECASE)
            )
            assert invoice_link.count() == 0 or not invoice_link.first.is_visible(), (
                "A Performa Invoice should not be available while shipping is Ask."
            )
            print(
                "Bank reservation verified: Payment Pending, shipping and final "
                "total are Ask, and Sales follow-up is displayed."
            )
            return self

        assert summary_total.lower() != "ask", (
            "Shipping has a known price, but the reservation Total Price is Ask."
        )
        assert not payment_total_requires_inquiry, (
            "Shipping has a known confirmation price, but the payment screen "
            "marked the total as requiring an inquiry."
        )
        assert self._normalize_price(summary_total) == self._normalize_price(
            expected_total
        ), (
            "Total Price changed after the Bank Transfer reservation: payment "
            f"screen showed {expected_total}, confirmation showed {summary_total}."
        )

        invoice_link = self.page.get_by_role(
            "link", name=re.compile(r"Download Performa Invoice", re.IGNORECASE)
        ).first
        invoice_link.wait_for(state="visible")
        invoice_href = invoice_link.get_attribute("href") or ""
        assert "/dashboard/download-resrve-invoice/" in invoice_href, (
            f"Unexpected Performa Invoice URL: {invoice_href!r}"
        )

        payment_proof = self.page.locator("a, button").filter(
            has_text=re.compile(r"Add Payment Proof", re.IGNORECASE)
        ).first
        payment_proof.wait_for(state="visible")
        assert payment_proof.is_enabled(), "Add Payment Proof button is disabled"

        print(
            "Bank reservation verified with matching total, downloadable Performa "
            "Invoice, and Add Payment Proof action."
        )
        return self
