from urllib.parse import urlparse


class MobileHelpPage:
    DESTINATIONS = (
        (
            "How to Buy",
            "/how-to-buy",
            "h1:has-text('How to Buy a Car with SAT')",
        ),
        (
            "Become a SAT Japan Dealer",
            "/dealers/sign-up",
            "#dealer-create-form",
        ),
        (
            "Become a Seller with SAT",
            "/seller-registration",
            "#sellerApplicationForm",
        ),
        (
            "Inquiry Form",
            "/inquiry-form",
            "h1:has-text('Inquiry Form:')",
        ),
        (
            "Vehicle Information Request",
            "/request-vehicle-information",
            "h1:has-text('Request Vehicle Information')",
        ),
        ("How to Pay", "/how-to-pay", "h1:has-text('How to Pay')"),
        (
            "Bank Information",
            "/bank-information",
            ".bank-info-top-hdr:has-text('Bank Information (USD)')",
        ),
        (
            "Track Your Order",
            "/track-your-order",
            "h1:has-text('Track Your Order')",
        ),
        ("FAQs", "/asked-questions", "#faq_search_input"),
        (
            "How to Pick the Right Used Car",
            "/how-to-choose",
            "h2:has-text('Overview')",
        ),
        (
            "Buying Vehicles Safely Guide",
            "/safety-with-sat",
            "text=How to Beware Of Fraudulent Activities",
        ),
    )

    def __init__(self, page):
        self.page = page

    def _main_menu(self):
        return self.page.locator("#sidebarmobile")

    def _help_menu(self):
        return self.page.locator("#offcanvascarhelp")

    def open_menu(self):
        help_menu = self._help_menu()
        if help_menu.is_visible():
            return self

        toggle = self.page.locator(
            "#menu_logo_mobile span[data-bs-target='#sidebarmobile']"
        )
        toggle.wait_for(state="visible")
        toggle.click()

        main_menu = self._main_menu()
        main_menu.wait_for(state="visible")
        help_link = main_menu.locator(
            "a.main-items-sidebar-content",
            has_text="Help",
        )
        if help_link.get_attribute("href") != "#offcanvascarhelp":
            raise AssertionError("The mobile Help menu target has changed.")
        help_link.click()
        help_menu.wait_for(state="visible")
        return self

    def _links(self):
        self.open_menu()
        return self._help_menu().get_by_role("link")

    def get_item_names(self):
        return [text.strip() for text in self._links().all_inner_texts()]

    def get_item_paths(self):
        return [
            urlparse(link.get_attribute("href") or "").path
            for link in self._links().all()
        ]

    def open_item(self, link_name, expected_path, ready_locator):
        self.open_menu()
        link = self._help_menu().get_by_role(
            "link",
            name=link_name,
            exact=True,
        )
        link.wait_for(state="visible")
        actual_path = urlparse(link.get_attribute("href") or "").path
        if actual_path != expected_path:
            raise AssertionError(
                f"Mobile Help link {link_name!r} changed: expected "
                f"{expected_path!r}, found {actual_path!r}."
            )

        link.click()
        self.page.wait_for_url(
            f"**{expected_path}*",
            wait_until="domcontentloaded",
        )
        self.page.locator(ready_locator).first.wait_for(state="visible")
        return self

    def assert_page_layout(
        self,
        page_name,
        ready_locator,
        *,
        require_mobile_header=True,
    ):
        layout = self.page.evaluate(
            """() => ({
                viewportWidth: window.visualViewport
                    ? window.visualViewport.width
                    : window.innerWidth,
                documentWidth: document.documentElement.scrollWidth,
                bodyWidth: document.body.scrollWidth
            })"""
        )
        tolerance = 1
        assert layout["documentWidth"] <= layout["viewportWidth"] + tolerance, (
            f"{page_name} has horizontal document overflow: {layout}"
        )
        assert layout["bodyWidth"] <= layout["viewportWidth"] + tolerance, (
            f"{page_name} has horizontal body overflow: {layout}"
        )
        if require_mobile_header:
            assert self.page.locator("#navbar_mobile_header").is_visible(), (
                f"{page_name} is missing the mobile header."
            )
        self.assert_elements_usable(
            self.page.locator(ready_locator).first,
            f"{page_name} primary content",
            require_enabled=False,
            check_overlap=False,
        )
        return layout

    def assert_elements_usable(
        self,
        elements,
        label,
        *,
        require_enabled=True,
        check_overlap=True,
    ):
        count = elements.count()
        assert count, f"No visible {label} were found."
        viewport_width = self.page.evaluate("window.innerWidth")

        for index in range(count):
            element = elements.nth(index)
            assert element.is_visible(), f"{label} {index + 1} is not visible."
            if require_enabled:
                assert element.is_enabled(), f"{label} {index + 1} is disabled."

            element.scroll_into_view_if_needed()
            state = element.evaluate(
                """node => {
                    const box = node.getBoundingClientRect();
                    const hit = document.elementFromPoint(
                        box.left + box.width / 2,
                        box.top + box.height / 2
                    );
                    const style = getComputedStyle(node);
                    return {
                        left: box.left,
                        right: box.right,
                        top: box.top,
                        bottom: box.bottom,
                        width: box.width,
                        height: box.height,
                        type: node.getAttribute('type') || '',
                        hasVisibleLabel: Boolean(
                            node.labels && Array.from(node.labels).some(
                                label => label.getClientRects().length > 0
                            )
                        ),
                        pointerEvents: style.pointerEvents,
                        visibility: style.visibility,
                        hitMatches: hit === node || node.contains(hit)
                    };
                }"""
            )
            assert state["width"] > 0 and state["height"] > 0, (
                f"{label} {index + 1} has zero rendered size: {state}"
            )
            if state["type"] in ("checkbox", "radio"):
                assert state["hasVisibleLabel"], (
                    f"{label} {index + 1} has no visible associated label."
                )
            assert state["left"] >= -1, (
                f"{label} {index + 1} is clipped on the left: {state}"
            )
            assert state["right"] <= viewport_width + 1, (
                f"{label} {index + 1} is clipped on the right: {state}"
            )
            assert state["pointerEvents"] != "none", (
                f"{label} {index + 1} cannot receive pointer input."
            )
            assert state["visibility"] == "visible", (
                f"{label} {index + 1} is visually hidden."
            )
            assert state["hitMatches"], (
                f"{label} {index + 1} is covered by another element: {state}"
            )

        if check_overlap and count > 1:
            boxes = elements.evaluate_all(
                """nodes => nodes.map((node, index) => {
                    const box = node.getBoundingClientRect();
                    const composite = node.closest('.iti');
                    return {
                        index: index + 1,
                        tag: node.tagName.toLowerCase(),
                        name: node.getAttribute('name') || '',
                        text: (node.innerText || node.value || '').trim(),
                        overlapGroup: composite
                            ? Array.from(document.querySelectorAll('.iti'))
                                .indexOf(composite)
                            : -1,
                        left: box.left,
                        right: box.right,
                        top: box.top + window.scrollY,
                        bottom: box.bottom + window.scrollY
                    };
                })"""
            )
            for index, current in enumerate(boxes):
                for following in boxes[index + 1 :]:
                    if (
                        current["overlapGroup"] >= 0
                        and current["overlapGroup"]
                        == following["overlapGroup"]
                    ):
                        continue
                    overlaps = not (
                        current["right"] <= following["left"]
                        or following["right"] <= current["left"]
                        or current["bottom"] <= following["top"]
                        or following["bottom"] <= current["top"]
                    )
                    assert not overlaps, (
                        f"{label} overlap on mobile: {current} and "
                        f"{following}."
                    )

        return count
