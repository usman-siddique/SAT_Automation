from urllib.parse import urlparse


class PrivacyPolicyPage:
    PRIVACY_PATH = "/privacy-policy"
    PRIVACY_HEADINGS = (
        "Privacy Policy",
        "What are Cookies?",
        "Types of Cookies We Use",
        "Essential Cookies",
        "Analytical Cookies",
        "Targeting Cookies",
        "Functionality Cookies",
        "More on Cookies",
        "How to Manage or Block Cookies",
        "Updates on Cookie Policy",
        "Contact us",
    )
    PRIVACY_EMAIL_LINKS = {
        "info@satjapan.com": "mailto:info@satjapan.com",
        "sales@satjapan.com": "mailto:sales@satjapan.com",
    }

    def __init__(self, page):
        self.page = page

    def _navigate_desktop(self, link_name, path, ready_selector):
        menu = self.page.locator("p.cnm-cls:has-text('About Us')").locator("..")
        menu.hover()
        link = menu.locator(".dropdown_content_header").get_by_role(
            "link", name=link_name, exact=True
        )
        link.wait_for(state="visible")
        link.click()
        self.page.wait_for_url(f"**{path}", wait_until="domcontentloaded")
        self.page.locator(ready_selector).wait_for(state="visible")
        assert urlparse(self.page.url).path.rstrip("/") == path

    def _navigate_mobile(self, path, ready_selector):
        self.page.locator(
            "#menu_logo_mobile span[data-bs-target='#sidebarmobile']"
        ).click()
        self.page.locator("#sidebarmobile a.main-items-sidebar-content").filter(
            has_text="About Us"
        ).click()
        link = self.page.locator(f"#offcanvascaroverview a[href$='{path}']")
        link.wait_for(state="visible")
        link.click()
        self.page.wait_for_url(f"**{path}", wait_until="domcontentloaded")
        self.page.locator(ready_selector).wait_for(state="visible")
        assert urlparse(self.page.url).path.rstrip("/") == path

    def go_to_privacy_policy(self):
        self._navigate_desktop(
            "Privacy Policy",
            self.PRIVACY_PATH,
            "section.cookies-polices-main h1.cookies-polices-comman-hdr",
        )

    def go_to_privacy_policy_mobile(self):
        self._navigate_mobile(
            self.PRIVACY_PATH, "h1.cookies-polices-comman-hdr"
        )

    def verify_privacy_title_and_headings(self):
        assert "Privacy Policy" in self.page.title(), (
            f"Privacy Policy has the wrong browser title: {self.page.title()}"
        )
        self._verify_headings(self.PRIVACY_HEADINGS, "Privacy Policy")

    def _verify_headings(self, headings, page_name):
        for heading in headings:
            visible = self.page.get_by_role(
                "heading", name=heading, exact=True
            ).filter(visible=True)
            assert visible.count() == 1, (
                f"{page_name} heading is missing or duplicated: {heading}"
            )

    def verify_privacy_email_links(self):
        for label, expected_href in self.PRIVACY_EMAIL_LINKS.items():
            link = self.page.locator("section.more-on-cookies-section").get_by_role(
                "link", name=label, exact=True
            ).filter(visible=True)
            assert link.count() == 1, f"Privacy Policy email link is missing: {label}"
            assert link.get_attribute("href") == expected_href, (
                f"Privacy Policy email link is incorrect: {label}"
            )

    def _verify_mobile_layout(self, content, page_links, page_name):
        layout = self.page.evaluate(
            """() => ({
                viewportWidth: visualViewport.width,
                documentWidth: document.documentElement.scrollWidth,
                bodyWidth: document.body.scrollWidth
            })"""
        )
        assert layout["viewportWidth"] == 390
        assert layout["documentWidth"] <= layout["viewportWidth"], (
            f"{page_name} has horizontal mobile overflow: {layout}"
        )
        assert layout["bodyWidth"] <= layout["viewportWidth"], (
            f"{page_name} body overflows on mobile: {layout}"
        )
        content_box = content.bounding_box()
        assert content_box["x"] >= 0
        assert content_box["x"] + content_box["width"] <= 390
        for index in range(page_links.count()):
            box = page_links.nth(index).bounding_box()
            assert box, f"{page_name} link has no mobile layout box"
            assert box["x"] >= 0 and box["x"] + box["width"] <= 390, (
                f"{page_name} link is clipped on mobile: {box}"
            )

    def verify_privacy_policy_mobile(self):
        self._verify_headings(self.PRIVACY_HEADINGS, "Privacy Policy")
        links = self.page.locator(
            "section.cookies-polices-main a:visible, "
            "section.more-on-cookies-section a:visible"
        )
        assert links.count() == 2
        self._verify_mobile_layout(
            self.page.locator("section.cookies-polices-main"),
            links,
            "Privacy Policy",
        )
