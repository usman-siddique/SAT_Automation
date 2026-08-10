from playwright.sync_api import Page


class CarDetailsPage:
    def __init__(self, page: Page):
        self.page = page

    def click_buy_now(self):
        """Open checkout and verify it belongs to the selected Used car."""
        selected_stock_id = self.page.url.rstrip("/").rsplit("/", 1)[-1].lower()
        assert selected_stock_id.startswith("sat-"), (
            f"Unexpected Used-car detail URL: {self.page.url}"
        )

        buy_now = self.page.locator("a.detail-btn.buy--now")
        buy_now.wait_for(state="visible")
        href = (buy_now.get_attribute("href") or "").lower()
        assert f"/checkout/{selected_stock_id}" in href, (
            f"Buy Now does not target checkout for {selected_stock_id}: {href}"
        )

        buy_now.click()
        self.page.wait_for_url(
            f"**/checkout/{selected_stock_id}**",
            wait_until="domcontentloaded",
        )
        print(f"Opened checkout for used car: {selected_stock_id.upper()}")
        return selected_stock_id
