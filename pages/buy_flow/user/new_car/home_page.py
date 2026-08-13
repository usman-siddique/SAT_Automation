import re

from playwright.sync_api import Page

from config import NEW_CAR_HOME_URL


class NewCarHomePage:
    def __init__(self, page: Page):
        self.page = page

    def open_from_header(self):
        """Open New Cars from the authenticated site's main navigation."""
        new_cars = self.page.locator("a[href*='/new-cars-home']").first
        new_cars.wait_for(state="visible")
        assert "/new-cars-home" in (new_cars.get_attribute("href") or ""), (
            "Header New Cars link does not target the New Car home page."
        )
        new_cars.click()
        self.page.wait_for_url(re.compile(r"/new-cars-home/?(?:\?.*)?$"))
        assert self.page.url.rstrip("/") == NEW_CAR_HOME_URL, (
            f"Unexpected New Car home URL: {self.page.url}"
        )
        print("Opened New Car home page from header")
        return self

    def show_cars(self):
        show_cars = self.page.locator(
            "button.search-btn-filter", has_text="Show Cars"
        ).first
        show_cars.wait_for(state="visible")
        assert show_cars.is_enabled(), "New Car Show Cars button is disabled"
        show_cars.click()
        self.page.wait_for_url(re.compile(r"/new-cars/?(?:\?.*)?$"))
        print("Opened New Car listing page")
        return self
