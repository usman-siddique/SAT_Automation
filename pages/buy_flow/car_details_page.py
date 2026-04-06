# pages/buy_flow/car_details_page.py
from playwright.sync_api import Page

class CarDetailsPage:
    def __init__(self, page: Page):
        self.page = page

    def click_buy_now(self):
        """Click the 'Buy Now' button on the car details page."""
        buy_now = self.page.locator("a.detail-btn.buy--now")
        buy_now.wait_for(state="visible")
        buy_now.click()
        print("✅ Clicked Buy Now")
        return self