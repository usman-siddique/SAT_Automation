from playwright.sync_api import Page


CHECKOUT_STABILIZATION_MS = 3000


class CheckoutPage:
    def __init__(self, page: Page):
        self.page = page

    def _wait_for_page_render(self):
        self.page.wait_for_load_state("domcontentloaded")
        loader = self.page.locator(".loader")
        if loader.count() > 0:
            loader.wait_for(state="hidden", timeout=30000)

    def select_services(self, service_ids: list):
        """Select services and allow shipping/price recalculation to finish."""
        self._wait_for_page_render()

        for service_id in service_ids:
            checkbox = self.page.locator(
                f"input.form-check-input[data-id='{service_id}']"
            ).first
            checkbox.wait_for(state="visible")
            if not checkbox.is_checked():
                checkbox.check()
                print(f"Checked service {service_id}")

        # Country, port, shipping, and totals update asynchronously.
        self.page.wait_for_timeout(CHECKOUT_STABILIZATION_MS)
        print("Checkout totals stabilization wait complete")
        return self

    def click_continue(self):
        """Continue only after the checkout page and totals have stabilized."""
        continue_btn = self.page.locator("button.checkout--btn.placeOrder")
        continue_btn.wait_for(state="visible")
        assert continue_btn.is_enabled(), "Checkout Continue button is disabled"
        continue_btn.click()
        print("Clicked Continue")
        return self
