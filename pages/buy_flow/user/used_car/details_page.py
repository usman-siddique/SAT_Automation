from playwright.sync_api import Page


class CarDetailsPage:
    def __init__(self, page: Page):
        self.page = page

    def _selected_stock_id(self):
        selected_stock_id = self.page.url.rstrip("/").rsplit("/", 1)[-1].lower()
        assert selected_stock_id.startswith("sat-"), (
            f"Unexpected Used-car detail URL: {self.page.url}"
        )
        return selected_stock_id

    def _checkout_link(self, selected_stock_id):
        expected_path = f"/checkout/{selected_stock_id}"
        buy_now_links = self.page.locator("a.detail-btn.buy--now")

        for index in range(buy_now_links.count()):
            link = buy_now_links.nth(index)
            if not link.is_visible():
                continue

            href = (link.get_attribute("href") or "").lower()
            if expected_path in href:
                return link

        return None

    def try_click_buy_now(self):
        """Open the matching checkout, or report stale/unavailable inventory."""
        selected_stock_id = self._selected_stock_id()
        checkout_link = self._checkout_link(selected_stock_id)

        if checkout_link is None:
            print(
                "Skipping Used car because its detail page has no matching "
                f"checkout: {selected_stock_id.upper()}"
            )
            return False

        checkout_link.click()
        self.page.wait_for_url(
            f"**/checkout/{selected_stock_id}**",
            wait_until="domcontentloaded",
        )
        print(f"Opened checkout for used car: {selected_stock_id.upper()}")
        return True

    def click_buy_now(self):
        """Open checkout and verify it belongs to the selected Used car."""
        selected_stock_id = self._selected_stock_id()

        assert self.try_click_buy_now(), (
            "Buy Now does not target checkout for "
            f"{selected_stock_id}: {self.page.url}"
        )
        return selected_stock_id
