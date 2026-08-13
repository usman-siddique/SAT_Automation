import re

from pages.buy_flow.user.new_car.variant import NewCarVariant
from pages.buy_flow.user.payment_page import PaymentPage


class NewCarPaymentPage(PaymentPage):
    def _payment_summary_price(self, label_text: str):
        label = self.page.locator("td.c-price-title", has_text=label_text).first
        label.wait_for(state="visible")
        return label.locator("xpath=ancestor::tr[1]").locator(
            "td.c-price"
        ).inner_text().strip()

    def verify_payment_summary(
        self,
        variant: NewCarVariant,
        expected_checkout_total: str,
    ):
        """Verify detail and checkout prices survive onto payment."""
        payment_car_price = self._payment_summary_price("Car Price")
        payment_total = self._payment_summary_price("Total Price")

        assert self._normalize_price(payment_car_price) == self._normalize_price(
            variant.car_price
        ), (
            "New Car price changed on payment page: details showed "
            f"{variant.car_price}, payment shows {payment_car_price}."
        )
        assert self._normalize_price(payment_total) == self._normalize_price(
            expected_checkout_total
        ), (
            "New Car total changed between checkout and payment: "
            f"{expected_checkout_total} -> {payment_total}."
        )
        print(
            f"New Car payment summary verified: car {payment_car_price}, "
            f"total {payment_total}"
        )
        return payment_total

    def verify_selected_paygent_total(self, expected_checkout_total: str):
        payment_total, total_requires_inquiry = self.get_selected_payment_total()
        assert self._normalize_price(payment_total) == self._normalize_price(
            expected_checkout_total
        ), (
            "New Car Paygent total changed after payment selection: "
            f"{expected_checkout_total} -> {payment_total}."
        )
        assert total_requires_inquiry, (
            "New Car Paygent total should indicate an inquiry while shipping is Ask."
        )
        return payment_total

    def verify_selected_bank_total(self, expected_checkout_total: str):
        payment_total, total_requires_inquiry = self.get_selected_payment_total()
        assert self._normalize_price(payment_total) == self._normalize_price(
            expected_checkout_total
        ), (
            "New Car Bank Transfer total changed after payment selection: "
            f"{expected_checkout_total} -> {payment_total}."
        )
        assert total_requires_inquiry, (
            "New Car Bank Transfer total should indicate an inquiry while "
            "shipping is Ask."
        )
        return payment_total

    def _submit_new_car_order(self, payment_name: str):
        proceed = self.page.locator("#submitPlaceOrder")
        proceed.wait_for(state="visible")
        assert proceed.is_enabled(), "Proceed to Checkout button is disabled"
        proceed.click()

        place_order = self.page.locator("button", has_text="Place Order").last
        place_order.wait_for(state="visible", timeout=10000)
        place_order.click()
        self.page.wait_for_url("**/new-car-order-summary/**", timeout=60000)
        print(f"Reached New Car {payment_name} order summary")
        return self

    def submit_new_car_paygent(self):
        return self._submit_new_car_order("Paygent")

    def submit_new_car_bank_transfer(self):
        return self._submit_new_car_order("Bank Transfer")

    def _verify_common_new_car_confirmation(
        self,
        variant: NewCarVariant,
        expected_status: str,
    ):
        success = self.page.get_by_text(
            re.compile(r"Thank you for placing an order with SAT", re.IGNORECASE)
        ).first
        success.wait_for(state="visible")

        track_order = self.page.locator("a:visible, button:visible").filter(
            has_text=re.compile(r"Track Your Order", re.IGNORECASE)
        ).first
        track_order.wait_for(state="visible")
        assert track_order.is_enabled(), "Track Your Order action is disabled"

        status = self._get_summary_value("Status")
        assert status.lower() == expected_status.lower(), (
            f"New Car status should be {expected_status}, found {status!r}."
        )

        final_car_price = self._get_summary_value("Car Price")
        assert self._normalize_price(final_car_price) == self._normalize_price(
            variant.car_price
        ), (
            "New Car price changed on confirmation: details showed "
            f"{variant.car_price}, confirmation shows {final_car_price}."
        )

        shipping_cost = self._get_summary_value("Shipping Cost")
        total_price = self._get_summary_value("Total Price")
        assert shipping_cost.lower() == "ask", (
            "New Car confirmation Shipping Cost should be Ask, "
            f"found {shipping_cost!r}."
        )
        assert total_price.lower() == "ask", (
            "New Car confirmation Total Price should be Ask, "
            f"found {total_price!r}."
        )

        assert re.search(r"/new-car-order-summary/\d+/?$", self.page.url), (
            f"Unexpected New Car confirmation URL: {self.page.url}"
        )
        return final_car_price

    def verify_new_car_confirmation(self, variant: NewCarVariant):
        final_car_price = self._verify_common_new_car_confirmation(
            variant,
            "Partial Payment",
        )
        print(
            "New Car Paygent confirmation verified: Partial Payment, matching "
            f"car price {final_car_price}, Shipping Ask, Total Ask"
        )
        return self

    def verify_new_car_bank_confirmation(self, variant: NewCarVariant):
        payment_instruction = self.page.get_by_text(
            re.compile(
                r"Please upload your bank payment proof to complete your order",
                re.IGNORECASE,
            )
        ).first
        payment_instruction.wait_for(state="visible")

        final_car_price = self._verify_common_new_car_confirmation(
            variant,
            "Pending",
        )

        payment_proof = self.page.locator("a:visible, button:visible").filter(
            has_text=re.compile(r"Add Payment Proof", re.IGNORECASE)
        ).first
        payment_proof.wait_for(state="visible")
        assert payment_proof.is_enabled(), "Add Payment Proof action is disabled"

        for bank_label in (
            "Bank Information",
            "Bank Name:",
            "Account Number:",
            "Branch Name:",
            "Swift Code:",
            "Bank address:",
        ):
            self.page.get_by_text(bank_label, exact=True).filter(
                visible=True
            ).first.wait_for(state="visible")

        print(
            "New Car Bank confirmation verified: Pending, matching car price "
            f"{final_car_price}, Shipping Ask, Total Ask, payment proof, and "
            "bank information"
        )
        return self
