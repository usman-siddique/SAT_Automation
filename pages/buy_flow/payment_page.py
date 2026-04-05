# pages/buy_flow/payment_page.py
from playwright.sync_api import Page

class PaymentPage:
    def __init__(self, page: Page):
        self.page = page

    def select_credit_card(self):
        # Wait for the radio button to be present and enabled
        credit_card = self.page.locator("input[name='payment'][value='paygent']")
        credit_card.wait_for(state="visible")
        # Ensure the radio button is not disabled
        credit_card.wait_for(state="enabled")
        credit_card.check()
        # Now wait for the card input fields container to become visible (the collapse expands)
        self.page.locator("#paygentBlock").wait_for(state="visible", timeout=10000)
        print("✅ Selected credit card payment")
        return self

    def fill_card_details(self, card_number: str, expiry: str, cvc: str):
        """Fill the credit card fields (direct inputs, no iframe)."""
        card_input = self.page.locator("#card_number")
        card_input.wait_for(state="visible")
        card_input.fill(card_number)

        expiry_input = self.page.locator("#expire_date")
        expiry_input.fill(expiry)

        cvc_input = self.page.locator("#cvc")
        cvc_input.fill(cvc)
        print("✅ Card details filled")
        return self

    def accept_terms(self):
        """Check the terms and conditions checkbox."""
        terms = self.page.locator("#term_conditions")
        terms.wait_for(state="visible")
        if not terms.is_checked():
            terms.check()
        print("✅ Accepted terms")
        return self

    def submit(self):
        """Click Proceed to Checkout, then the popup Place Order button, and wait for order summary."""
        # Step 1: Click "Proceed to Checkout"
        proceed = self.page.locator("#submitPlaceOrder")
        proceed.wait_for(state="visible")
        proceed.click()
        print("✅ Clicked Proceed to Checkout")

        # Step 2: Handle the popup modal with "Place Order" button
        place_order_btn = self.page.locator("button:has-text('Place Order')")
        place_order_btn.wait_for(state="visible", timeout=10000)
        place_order_btn.click()
        print("✅ Clicked Place Order in popup")

        # Step 3: Wait for the order summary page (3DS may take a few seconds)
        self.page.wait_for_url("**/order-summary/**", timeout=60000)
        print("✅ Reached order summary page")
        return self

    def verify_order_confirmation(self):
        """Verify the order summary page content."""
        success_heading = self.page.locator("h1.main-title:has-text('Thank you for placing an order')")
        success_heading.wait_for(state="visible")
        track_btn = self.page.locator("button.track-ordr-btn:has-text('Track Your Order')")
        track_btn.wait_for(state="visible")
        print("✅ Order confirmation verified")
        return self