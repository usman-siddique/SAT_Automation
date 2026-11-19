from urllib.parse import urlparse


class TermsConditionsPage:
    TERMS_PATH = "/terms-condition"
    TERMS_HEADINGS = (
        "Terms and Conditions",
        "Anti-Corruption",
        "Warranty and Liability",
        "Terms that are Non-English",
        "Other Agreements",
        "Miscellaneous",
        "Submission",
        "Data Handling",
        "Security Export Control",
        "Abuse",
        "Transactions",
        "Anti-Social Forces",
    )
    VEHICLE_AGREEMENT_FILE = "vehicle-sales-agreement.pdf"

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

    def go_to_terms_and_conditions(self):
        self._navigate_desktop(
            "Terms and Conditions", self.TERMS_PATH, "h1.term-main-hdr"
        )

    def go_to_terms_and_conditions_mobile(self):
        self._navigate_mobile(self.TERMS_PATH, "h1.term-main-hdr")

    def verify_terms_title_and_headings(self):
        assert self.page.title() == (
            "SAT Japan Terms & Conditions | Vehicle Purchase Terms"
        )
        self._verify_headings(self.TERMS_HEADINGS, "Terms and Conditions")

    def _verify_headings(self, headings, page_name):
        for heading in headings:
            visible = self.page.get_by_role(
                "heading", name=heading, exact=True
            ).filter(visible=True)
            assert visible.count() == 1, (
                f"{page_name} heading is missing or duplicated: {heading}"
            )

    def verify_terms_vehicle_agreement_pdf(self):
        link = self.page.get_by_role(
            "link", name="vehicle purchase agreement", exact=True
        ).filter(visible=True)
        assert link.count() == 1, "Vehicle purchase agreement link is missing"
        href = link.get_attribute("href")
        assert urlparse(href).path.endswith(self.VEHICLE_AGREEMENT_FILE)
        assert link.get_attribute("target") == "_blank"

        response = self.page.request.get(
            href, fail_on_status_code=False, timeout=30000
        )
        assert response.status == 200, (
            f"Vehicle agreement PDF returned HTTP {response.status}"
        )
        assert "application/pdf" in response.headers.get("content-type", ""), (
            "Vehicle agreement is not served as application/pdf"
        )
        body = response.body()
        assert len(body) > 1000, "Vehicle agreement PDF is unexpectedly small"
        assert body.startswith(b"%PDF"), (
            "Vehicle agreement does not have a valid PDF signature"
        )

        with self.page.context.expect_page(timeout=30000) as pdf_page_info:
            link.click()
        pdf_page = pdf_page_info.value
        try:
            pdf_page.wait_for_url(
                f"**/{self.VEHICLE_AGREEMENT_FILE}",
                wait_until="domcontentloaded",
                timeout=30000,
            )
            assert urlparse(pdf_page.url).path.endswith(
                self.VEHICLE_AGREEMENT_FILE
            ), f"Vehicle agreement opened the wrong page: {pdf_page.url}"
        finally:
            if not pdf_page.is_closed():
                pdf_page.close()

    def _verify_mobile_layout(self, content, page_links, page_name):
        layout = self.page.evaluate(
            """() => ({
                viewportWidth: visualViewport.width,
                documentWidth: document.documentElement.scrollWidth,
                bodyWidth: document.body.scrollWidth
            })"""
        )
        assert layout["viewportWidth"] > 0
        assert layout["documentWidth"] <= layout["viewportWidth"], (
            f"{page_name} has horizontal mobile overflow: {layout}"
        )
        assert layout["bodyWidth"] <= layout["viewportWidth"], (
            f"{page_name} body overflows on mobile: {layout}"
        )
        content_box = content.bounding_box()
        assert content_box["x"] >= 0
        assert (
            content_box["x"] + content_box["width"]
            <= layout["viewportWidth"]
        )
        for index in range(page_links.count()):
            box = page_links.nth(index).bounding_box()
            assert box, f"{page_name} link has no mobile layout box"
            assert (
                box["x"] >= 0
                and box["x"] + box["width"] <= layout["viewportWidth"]
            ), (
                f"{page_name} link is clipped on mobile: {box}"
            )

    def verify_terms_and_conditions_mobile(self):
        self._verify_headings(self.TERMS_HEADINGS, "Terms and Conditions")
        pdf_link = self.page.get_by_role(
            "link", name="vehicle purchase agreement", exact=True
        ).filter(visible=True)
        assert pdf_link.count() == 1
        content = self.page.locator("h1.term-main-hdr").locator(
            "xpath=ancestor::section[1]"
        )
        self._verify_mobile_layout(content, pdf_link, "Terms and Conditions")
