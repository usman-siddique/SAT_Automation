# pages/buy_flow/checkout_page.py
from playwright.sync_api import Page

class CheckoutPage:
    def __init__(self, page: Page):
        self.page = page

    def select_services(self, service_ids: list):
        """Select service checkboxes by their data-id attributes (uses .first to avoid strict mode)."""
        for sid in service_ids:
            checkbox = self.page.locator(f"input.form-check-input[data-id='{sid}']").first
            checkbox.wait_for(state="visible")
            if not checkbox.is_checked():
                checkbox.check()
                print(f"✅ Checked service {sid}")
        return self

    def click_continue(self):
        """Click the Continue (Place Order) button on the checkout page."""
        continue_btn = self.page.locator("button.checkout--btn.placeOrder")
        continue_btn.wait_for(state="visible")
        continue_btn.click()
        print("✅ Clicked Continue")
        return self