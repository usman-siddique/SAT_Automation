from urllib.parse import urlparse

from playwright.sync_api import TimeoutError as PlaywrightTimeoutError


class HelpPage:
    MENU_ITEMS = (
        ("How to Buy", "/how-to-buy"),
        ("Become a SAT Japan Dealer", "/dealers/join-as-dealer"),
        ("Inquiry Form", "/inquiry-form"),
        ("Vehicle Information Request", "/request-vehicle-information"),
        ("How to Pay", "/how-to-pay"),
        ("Bank Information", "/bank-information"),
        ("Track Your Order", "/track-your-order"),
        ("FAQ’s", "/faq"),
        ("How to Pick the Right Used Car", "/how-to-choose"),
        ("Buying Vehicles Safely Guide", "/safety-with-sat"),
    )
    LOAD_ATTEMPTS = 3

    def __init__(self, page):
        self.page = page

    def _menu(self):
        return self.page.locator("p.cnm-cls", has_text="Help").first.locator("..")

    def _dropdown_links(self):
        menu = self._menu()
        menu.hover()
        dropdown = menu.locator(".dropdown_content_header")
        dropdown.wait_for(state="visible")
        return dropdown.get_by_role("link")

    def get_menu_item_names(self):
        return [text.strip() for text in self._dropdown_links().all_inner_texts()]

    def get_menu_item_paths(self):
        paths = []
        for link in self._dropdown_links().all():
            href = link.get_attribute("href") or ""
            paths.append(urlparse(href).path)
        return paths

    def open_menu_item(
        self,
        link_name,
        expected_path,
        ready_locator,
        expected_final_path=None,
    ):
        menu = self._menu()
        menu.hover()
        dropdown = menu.locator(".dropdown_content_header")
        link = dropdown.get_by_role("link", name=link_name, exact=True)
        link.wait_for(state="visible")

        href = link.get_attribute("href") or ""
        actual_path = urlparse(href).path
        if actual_path != expected_path:
            raise AssertionError(
                f"Help link {link_name!r} changed: expected path "
                f"{expected_path!r}, found {actual_path!r}."
            )

        try:
            link.click(timeout=10000)
        except PlaywrightTimeoutError:
            menu.hover()
            link.wait_for(state="visible")
            link.click(force=True)
        final_path = expected_final_path or expected_path
        self.page.wait_for_url(f"**{final_path}*")

        for attempt in range(1, self.LOAD_ATTEMPTS + 1):
            try:
                self.page.locator(ready_locator).first.wait_for(
                    state="visible", timeout=10000
                )
                return self
            except PlaywrightTimeoutError:
                if attempt == self.LOAD_ATTEMPTS:
                    raise
                self.page.reload(wait_until="domcontentloaded")

        return self
