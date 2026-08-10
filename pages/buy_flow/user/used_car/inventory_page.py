from playwright.sync_api import Page


class UsedCarsPage:
    def __init__(self, page: Page):
        self.page = page

    def open(self, listing_url: str):
        """Open the configured unreserved Used inventory and verify its tab."""
        if not listing_url:
            raise AssertionError(
                "The configured Used Car inventory URL is missing. Check the "
                "selected BASE_URL and Buy Flow path settings."
            )

        self.page.goto(listing_url, wait_until="domcontentloaded")
        self.page.locator(".loader").wait_for(state="hidden", timeout=30000)

        used_tab = self.page.locator(".nav-link", has_text="Used").first
        auction_tab = self.page.locator(".nav-link", has_text="Auction").first
        used_tab.wait_for(state="visible")

        assert "active" in (used_tab.get_attribute("class") or ""), (
            "Used inventory tab is not active. Check the configured inventory path."
        )
        assert "active" not in (auction_tab.get_attribute("class") or ""), (
            "Auction inventory became active; refusing to select an auction car."
        )
        assert "/auction_cars" not in self.page.url, (
            "Buy flow opened the Auction inventory instead of Used inventory."
        )
        return self

    def select_any_available_used_car(self):
        """Select the first visible, unreserved Used car with Inquire Now."""
        for title in self.page.locator("a.search-car--title").all():
            if not title.is_visible():
                continue

            href = title.get_attribute("href") or ""
            card = title.locator(
                "xpath=./ancestor::div[contains(@class, 'car--detail')]"
            ).first
            card_text = card.inner_text().lower()
            inquire_button = card.locator(
                "button.btnCarPriceQuote", has_text="Inquire Now"
            )

            is_available_used_car = (
                "/auction_cars" not in href
                and "sold" not in card_text
                and "reserved" not in card_text
                and inquire_button.count() > 0
                and inquire_button.is_visible()
            )
            if not is_available_used_car:
                continue

            stock_id = href.rstrip("/").rsplit("/", 1)[-1]
            title.click()
            self.page.wait_for_url(
                f"**/used-cars/**/{stock_id}",
                wait_until="domcontentloaded",
            )
            assert "/auction_cars" not in self.page.url, (
                "Selected vehicle redirected to Auction inventory."
            )
            print(f"Selected available used car: {stock_id.upper()}")
            return stock_id

        raise AssertionError(
            "No visible, unreserved Used car with Inquire Now was available "
            f"on {self.page.url}."
        )
