import re

from playwright.sync_api import Page


class NewCarListingPage:
    def __init__(self, page: Page):
        self.page = page

    def select_make(self, make: str):
        make_control = self.page.locator("button.satSelectBtn").filter(
            has=self.page.locator(
                "span.type", has_text=re.compile(r"^Make$", re.IGNORECASE)
            )
        ).first
        make_control.wait_for(state="visible")
        make_control.click()

        make_menu = self.page.locator("#make_list")
        make_menu.wait_for(state="visible")
        make_option = make_menu.get_by_text(make, exact=True).first
        make_option.wait_for(state="visible")
        make_path = make_option.get_attribute("data-value") or ""
        assert make_path, f"No route value was configured for New Car make {make!r}"
        make_option.click()

        self.page.wait_for_url(re.compile(rf"/new-cars/{re.escape(make_path)}(?:\?.*)?$"))
        selected_make = make_control.locator("span.button-text")
        selected_make.wait_for(state="visible")
        assert selected_make.inner_text().strip().lower() == make.lower(), (
            f"Expected New Car make {make!r}, found {selected_make.inner_text()!r}."
        )
        print(f"Applied New Car make filter: {make}")
        return self

    def select_user_car(self, make: str, model_slug: str):
        """Open a deterministic user car after verifying Inquire Now."""
        title = self.page.locator(
            f"a.search-car--title[href*='/new-cars/'][href$='/{model_slug}']"
        ).first
        title.wait_for(state="visible")
        assert make.lower() in title.inner_text().lower(), (
            f"Selected New Car is not from the {make} listing: {title.inner_text()!r}"
        )

        card = title.locator(
            "xpath=ancestor::div[contains(@class, 'car--detail')][1]"
        )
        inquire = card.locator(
            "button.btnCarPriceQuote[data-car-type='new_car']",
            has_text="Inquire Now",
        )
        inquire.wait_for(state="visible")
        assert inquire.is_enabled(), (
            "Inquire Now is not available for the selected User New Car."
        )

        selected_title = title.inner_text().strip()
        title.click()
        self.page.wait_for_url(re.compile(rf"/new-cars/.+/{re.escape(model_slug)}/?$"))
        print(f"Selected User New Car: {selected_title}")
        return selected_title
