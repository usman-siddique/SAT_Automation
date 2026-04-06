# pages/buy_flow/used_cars_page.py
from playwright.sync_api import Page

class UsedCarsPage:
    def __init__(self, page: Page):
        self.page = page

    def open(self, unreserved: bool = True):
        """Open the used cars listing page, optionally filtering to unreserved cars."""
        url = "https://development.satjapan.info/used-cars?sort_by=new_arrival&per_page=25&page=1"
        if unreserved:
            url += "&unreserved=1"
        self.page.goto(url, wait_until="domcontentloaded")
        # Wait for the loader to disappear
        self.page.locator(".loader").wait_for(state="hidden", timeout=10000)
        # Short wait for AJAX content to settle (acceptable for dynamic lists)
        self.page.wait_for_timeout(1500)
        return self

    def select_any_car_with_inquire_now(self):
        """Find the first car card that has an 'Inquire Now' button and click its title link."""
        car_titles = self.page.locator("a.search-car--title").all()
        for title in car_titles:
            # Locate the parent car card (adjust XPath as needed)
            card = title.locator("xpath=./ancestor::div[contains(@class, 'car--detail')]")
            if card.locator("button.btnCarPriceQuote").count() > 0:
                title.click()
                print("✅ Selected car with Inquire Now button")
                return True
        raise Exception("No car with 'Inquire Now' button found")