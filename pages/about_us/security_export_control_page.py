from urllib.parse import urlparse


class SecurityExportControlPage:
    PATH = "/security-export-control"
    TITLE = "Ensuring International Security and Compliance on Cars - SAT Japan"
    SECTIONS = (
        (
            "Maintenance of International Security and Peace",
            "SAT is obliged to follow all applicable local, state, federal, "
            "and international rules, regulations, and protocols in regard "
            "to its participation in the maintenance of international "
            "security and peace, regional export control association, "
            "anti-terrorism, and all export controls, including list controls "
            "and catch-all controls in order to prevent the development of "
            "weapons for mass destruction. We stay informed about export "
            "control laws and regulations of the countries we export vehicles to.",
        ),
        (
            "Custom Documentation and Declarations",
            "Completion and submission of custom documentation are critical. "
            "Accurate declaration in regard to the nature of goods, deliberate "
            "use, and end-user detail is ensured with applicable export "
            "control regulations.",
        ),
    )
    DESKTOP_IMAGES = (
        "security-export-new-banner.webp",
        "security-export-control-img1.webp",
        "security-export-control-img2.webp",
    )
    MOBILE_IMAGES = (
        "security-export-mob-banner.webp",
        "security-export-control-mob-img1.webp",
        "security-export-control-mob-img2.webp",
    )

    def __init__(self, page):
        self.page = page

    def _content(self):
        return self.page.locator("section.security-export-control")

    def _wait_until_ready(self):
        self.page.wait_for_url(
            "**/security-export-control", wait_until="domcontentloaded"
        )
        self.page.get_by_role(
            "heading",
            name="Maintenance of International Security and Peace",
            exact=True,
        ).wait_for(state="visible")
        assert urlparse(self.page.url).path.rstrip("/") == self.PATH

    def go_to_security_export_control(self):
        menu = self.page.locator("p.cnm-cls:has-text('About Us')").locator("..")
        menu.hover()
        link = menu.locator(".dropdown_content_header").get_by_role(
            "link", name="Security Export", exact=True
        )
        link.wait_for(state="visible")
        assert urlparse(link.get_attribute("href")).path.rstrip("/") == self.PATH
        link.click()
        self._wait_until_ready()

    def go_to_security_export_control_mobile(self):
        self.page.locator(
            "#menu_logo_mobile span[data-bs-target='#sidebarmobile']"
        ).click()
        self.page.locator("#sidebarmobile a.main-items-sidebar-content").filter(
            has_text="About Us"
        ).click()
        link = self.page.locator(
            "#offcanvascaroverview a[href$='/security-export-control']"
        )
        link.wait_for(state="visible")
        link.click()
        self._wait_until_ready()

    def _verify_content(self):
        content = self._content()
        assert content.count() == 1, "Security Export Control content is missing"
        cards = content.locator(".security-export-card-main")
        assert cards.count() == len(self.SECTIONS), (
            f"Expected {len(self.SECTIONS)} compliance cards, found {cards.count()}"
        )
        for index, (heading, expected_copy) in enumerate(self.SECTIONS):
            card = cards.nth(index)
            assert card.get_by_role(
                "heading", name=heading, exact=True
            ).is_visible(), f"Security Export Control heading is missing: {heading}"
            actual_copy = " ".join(
                card.locator("p.security-export-card-para").inner_text().split()
            )
            assert actual_copy == expected_copy, (
                f"Security Export Control copy changed under: {heading}"
            )
        assert content.locator("a").count() == 0, (
            "Security Export Control now contains links that need destination checks"
        )
        return cards

    def _verify_images(self, selector, expected_files, label):
        images = self._content().locator(selector)
        assert images.count() == len(expected_files), (
            f"Expected {len(expected_files)} {label} images, found {images.count()}"
        )
        for index, expected_file in enumerate(expected_files):
            image = images.nth(index)
            image.scroll_into_view_if_needed()
            assert expected_file in (image.get_attribute("src") or ""), (
                f"{label} image source changed: {expected_file}"
            )
            assert image.evaluate(
                "element => element.complete && element.naturalWidth > 0"
            ), f"{label} image did not load: {expected_file}"
        return images

    def verify_desktop_content_and_media(self):
        assert self.page.title() == self.TITLE
        self._verify_content()
        self._verify_images(
            ".security-export-control-new-banner:visible, "
            ".security-export-card-img:visible",
            self.DESKTOP_IMAGES,
            "desktop",
        )
        assert self._content().locator(
            ".security-export-control-mob-new-banner:visible, "
            ".security-export-card-mob-img:visible"
        ).count() == 0, "Mobile Security Export media is visible on desktop"

    def verify_mobile_content_media_and_layout(self):
        assert self.page.locator("#navbar_mobile_header").is_visible(), (
            "Security Export Control mobile header is missing"
        )
        cards = self._verify_content()
        images = self._verify_images(
            ".security-export-control-mob-new-banner:visible, "
            ".security-export-card-mob-img:visible",
            self.MOBILE_IMAGES,
            "mobile",
        )
        assert self._content().locator(
            ".security-export-control-new-banner:visible, "
            ".security-export-card-img:visible"
        ).count() == 0, "Desktop Security Export media is visible on mobile"

        layout = self.page.evaluate(
            """() => ({
                screenWidth: screen.width,
                visualWidth: visualViewport.width,
                documentWidth: document.documentElement.scrollWidth,
                bodyWidth: document.body.scrollWidth
            })"""
        )
        assert layout["screenWidth"] == layout["visualWidth"] == 390, (
            f"Security Export Control mobile viewport is incorrect: {layout}"
        )
        assert layout["documentWidth"] <= layout["visualWidth"], (
            f"Security Export Control has horizontal overflow: {layout}"
        )
        assert layout["bodyWidth"] <= layout["visualWidth"], (
            f"Security Export Control body has horizontal overflow: {layout}"
        )

        boxes = cards.evaluate_all(
            """elements => elements.map(element => {
                const box = element.getBoundingClientRect();
                return {x: box.x, y: box.y, width: box.width, height: box.height};
            })"""
        )
        for box in boxes:
            assert box["x"] >= 0 and box["x"] + box["width"] <= 390, (
                f"Security Export card is clipped on mobile: {box}"
            )
        assert boxes[0]["y"] + boxes[0]["height"] <= boxes[1]["y"], (
            "Security Export cards overlap on mobile"
        )
        for index in range(images.count()):
            box = images.nth(index).bounding_box()
            assert box and box["x"] >= 0 and box["x"] + box["width"] <= 390, (
                f"Security Export image is clipped on mobile: {box}"
            )
