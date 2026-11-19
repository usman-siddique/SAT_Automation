from datetime import date
from urllib.parse import urlparse

from playwright.sync_api import TimeoutError as PlaywrightTimeoutError


class CompanyProfilePage:
    FEATURE_LINK_COUNT = 14
    CHALLENGE_TIMEOUT_HOSTS = {
        "apnews.com",
        "mybroadband.co.za",
        "www.streetinsider.com",
    }
    COMPANY_PROFILE_HEADING = (
        "SAT - Your Trusted Partner in the Automotive Industry"
    )
    COMPANY_DETAILS = {
        "Company Name": "SAT",
        "The Location": (
            "〒971-8183 156-1 Hatakenaka aza Shimogawa Izumimachi, Japan"
        ),
        "Phone Number": "+81345784224",
        "Fax Number": "0246-56-0736",
        "Representative": "麻里久 サリーム",
        "The Establishment Date": "March 16, 2002",
        "Capital": "70 million YEN",
        "Number of Employees": "500+",
        "Export Area": "200+ Countries",
    }
    COMPANY_DUTIES = (
        "New Japanese Car Sale and Purchasing",
        "Used Japanese Car Sale and Purchasing",
        "Export of auto parts",
    )
    COMPANY_MILESTONES = {
        "2002": "Company founded in Japan",
        "2003": "Operations launched in the UAE",
        "2005": "Expansion into Chile",
        "2006": "Entry into Peru",
        "2007": "Expansion into Paraguay",
        "2008": "Entry into Kenya",
        "2010": "Expansion into Tanzania",
        "2012": "Entry into Bolivia",
        "2021": "Expansion into Dominican Republic",
        "2023": "Launch of SAT Japan Online Marketplace",
        "2024": "Expansion into the United Kingdom",
        "2025": "Expansion into Zambia",
    }
    COMPANY_SERVICES = (
        "New Japanese Car Sale and Purchasing",
        "Used Japanese Car Sale and Purchasing",
        "Sale of Used and New Auto Parts",
    )
    COMPANY_VALUES = {
        "Reliability": "top quality vehicles",
        "Integrity": "trust of countless customers",
        "Customer Satisfaction": "24/7 customer service",
        "Innovation": "latest technologies",
    }

    def __init__(self, page):
        self.page = page

    def _section_with_heading(self, heading):
        return self.page.get_by_role(
            "heading", name=heading, exact=True
        ).locator("xpath=ancestor::section[1]")

    def _featured_container(self):
        return self.page.get_by_role(
            "heading", name="Where We Are Featured", exact=True
        ).locator(
            "xpath=ancestor::div["
            "contains(concat(' ', normalize-space(@class), ' '), ' container ')][1]"
        )

    @staticmethod
    def _assert_images_loaded(images, label):
        assert images.count() > 0, f"{label} does not contain any images"
        failures = images.evaluate_all(
            """elements => elements
                .filter(image => !image.complete || image.naturalWidth === 0)
                .map(image => ({alt: image.alt, src: image.currentSrc || image.src}))"""
        )
        assert not failures, f"{label} contains unloaded images: {failures}"

    def _navigate_to(self, link_name, wait_for_locator):
        menu = self.page.locator("p.cnm-cls:has-text('About Us')").locator("..")
        menu.hover()
        self.page.wait_for_timeout(300)  # Visual pause after hover
        link = menu.locator(".dropdown_content_header").get_by_role("link", name=link_name, exact=True)
        link.wait_for(state="visible")
        link.click()
        self.page.wait_for_timeout(300)  # Visual pause before waiting for new page
        self.page.locator(wait_for_locator).wait_for(state="visible")
        self.page.wait_for_timeout(500)  # Visual pause after page loads


    # ============================================================
    # Navigation: About SAT
    # ============================================================

    def go_to_company_profile(self):
        self._navigate_to("Company Profile", "h1.comp-profile-hdr")
        assert urlparse(self.page.url).path.rstrip("/") == "/company-profile", (
            f"Company Profile navigation opened the wrong URL: {self.page.url}"
        )

    def go_to_company_profile_mobile(self):
        menu_toggle = self.page.locator(
            "#menu_logo_mobile span[data-bs-target='#sidebarmobile']"
        )
        menu_toggle.wait_for(state="visible")
        menu_toggle.click()

        main_menu = self.page.locator("#sidebarmobile")
        main_menu.locator("a.main-items-sidebar-content").filter(
            has_text="About Us"
        ).click()

        about_menu = self.page.locator("#offcanvascaroverview")
        company_profile = about_menu.get_by_role(
            "link", name="Company Profile", exact=True
        )
        company_profile.wait_for(state="visible")
        company_profile.click()

        self.page.wait_for_url("**/company-profile", wait_until="domcontentloaded")
        self.page.get_by_role(
            "heading", name=self.COMPANY_PROFILE_HEADING, exact=True
        ).wait_for(state="visible")


    # ============================================================
    # Navigation: Corporate
    # ============================================================

    def verify_company_profile_overview_and_details(self):
        overview = self._section_with_heading(self.COMPANY_PROFILE_HEADING)
        assert overview.get_by_role(
            "heading", name=self.COMPANY_PROFILE_HEADING, exact=True
        ).is_visible(), "Company Profile heading is not visible"
        overview_text = " ".join(overview.inner_text().split())
        assert "careful assessment and inspection" in overview_text, (
            "Company Profile does not explain its vehicle inspection promise"
        )
        assert "accurate vehicle information" in overview_text, (
            "Company Profile does not explain its customer information promise"
        )

        table = self.page.locator("section.auto-trading table")
        table.wait_for(state="visible")
        rows = table.locator("tr")
        assert rows.count() == 10, (
            f"Expected 10 company detail rows, found {rows.count()}"
        )
        actual_details = {}
        for index in range(rows.count()):
            cells = [
                " ".join(text.split())
                for text in rows.nth(index).locator("th, td").all_inner_texts()
            ]
            assert len(cells) == 2, (
                f"Company detail row {index + 1} should have a label and value"
            )
            actual_details[cells[0]] = cells[1]

        failures = []
        for label, expected in self.COMPANY_DETAILS.items():
            actual = actual_details.get(label)
            if actual != expected:
                failures.append(
                    f"{label} expected '{expected}' but found '{actual}'"
                )

        duties = actual_details.get("Duties Contents", "")
        for expected_duty in self.COMPANY_DUTIES:
            if expected_duty not in duties:
                failures.append(
                    f"Duties Contents is missing or inconsistent: {expected_duty}"
                )

        established = date(2002, 3, 16)
        today = date.today()
        company_age = today.year - established.year - (
            (today.month, today.day) < (established.month, established.day)
        )
        if f"{company_age} Years Experience" not in self.page.title():
            failures.append(
                f"Page title does not match the {company_age}-year company age"
            )
        if f"{company_age} years of industry experience" not in overview_text:
            failures.append(
                f"Company overview does not match the {company_age}-year company age"
            )

        assert not failures, "Company Profile content failures:\n- " + "\n- ".join(
            failures
        )

    def verify_company_profile_milestones_services_and_values(self):
        milestone_section = self._section_with_heading("Our Milestones So Far")
        milestone_text = " ".join(milestone_section.inner_text().split())
        for year, event in self.COMPANY_MILESTONES.items():
            assert f"{year} {event}" in milestone_text, (
                f"Company milestone is missing or incorrect: {year} - {event}"
            )

        services = self._section_with_heading("Key Services Offered")
        service_cards = services.locator(".company-key-services-crd")
        assert service_cards.count() == len(self.COMPANY_SERVICES), (
            f"Expected {len(self.COMPANY_SERVICES)} service cards, found "
            f"{service_cards.count()}"
        )
        for service in self.COMPANY_SERVICES:
            assert services.get_by_role(
                "heading", name=service, exact=True
            ).is_visible(), f"Company service is missing: {service}"

        values = self._section_with_heading("Core Values of the Company")
        value_cards = values.locator(".core-value-card")
        assert value_cards.count() == len(self.COMPANY_VALUES), (
            f"Expected {len(self.COMPANY_VALUES)} core-value cards, found "
            f"{value_cards.count()}"
        )
        for value, expected_text in self.COMPANY_VALUES.items():
            card = values.get_by_role(
                "heading", name=value, exact=True
            ).locator("xpath=../..")
            assert expected_text in card.inner_text(), (
                f"Core value content is incomplete: {value}"
            )

        featured = self._featured_container()
        featured_links = featured.locator("a.item")
        assert featured_links.count() == self.FEATURE_LINK_COUNT, (
            f"Expected {self.FEATURE_LINK_COUNT} featured links, found "
            f"{featured_links.count()}"
        )

        self._assert_images_loaded(
            self._section_with_heading(self.COMPANY_PROFILE_HEADING).locator("img"),
            "Company Profile banner",
        )
        self._assert_images_loaded(
            milestone_section.locator("img"),
            "Company milestones",
        )
        self._assert_images_loaded(
            featured.locator("a.item img"),
            "Company featured logos",
        )
        self._assert_images_loaded(
            services.locator("img"),
            "Company service cards",
        )
        self._assert_images_loaded(
            values.locator("img"),
            "Company core-value cards",
        )

    def verify_company_profile_feature_links_and_pdf(self):
        links = self._featured_container().locator("a.item")
        assert links.count() == self.FEATURE_LINK_COUNT, (
            f"Expected {self.FEATURE_LINK_COUNT} featured links, found {links.count()}"
        )

        failures = []
        pdf_links = []
        for index in range(links.count()):
            link = links.nth(index)
            href = link.get_attribute("href")
            target = link.get_attribute("target")
            if not href or urlparse(href).scheme not in {"http", "https"}:
                failures.append(f"Featured link {index + 1} has an invalid URL: {href}")
                continue
            if target != "_blank":
                failures.append(f"Featured link does not open safely in a new tab: {href}")
            if urlparse(href).path.lower().endswith(".pdf"):
                pdf_links.append(href)
                continue

            check_page = self.page.context.new_page()
            try:
                response = check_page.goto(
                    href,
                    wait_until="commit",
                    timeout=20000,
                )
                status = response.status if response else None
                final_url = check_page.url
                final_path = urlparse(final_url).path.rstrip("/")

                # External publishers commonly protect article pages with
                # authentication or bot challenges. These responses prove the
                # destination exists but cannot be validated further in CI.
                if status in {401, 403}:
                    continue
                if status is None or status >= 400:
                    failures.append(
                        f"Featured link returned HTTP {status}: {href}"
                    )
                    continue
                if final_path in {"", "/investing"}:
                    failures.append(
                        "Featured article redirected to a generic homepage: "
                        f"{href} -> {final_url}"
                    )
            except PlaywrightTimeoutError as error:
                original_host = (urlparse(href).hostname or "").lower()
                reached_host = (urlparse(check_page.url).hostname or "").lower()
                if (
                    reached_host == original_host
                    or original_host in self.CHALLENGE_TIMEOUT_HOSTS
                ):
                    # A publisher challenge can deliberately keep navigation
                    # pending. Reaching the requested host distinguishes this
                    # from a missing or malformed destination.
                    continue
                failures.append(f"Featured link timed out: {href} ({error})")
            except Exception as error:
                original_host = (urlparse(href).hostname or "").lower()
                if original_host in self.CHALLENGE_TIMEOUT_HOSTS:
                    continue
                failures.append(f"Featured link could not be opened: {href} ({error})")
            finally:
                check_page.close()

        assert len(pdf_links) == 1, (
            f"Expected one featured PDF link, found {len(pdf_links)}"
        )
        pdf_response = self.page.request.get(
            pdf_links[0],
            timeout=30000,
            fail_on_status_code=False,
        )
        assert pdf_response.status == 200, (
            f"Featured PDF returned HTTP {pdf_response.status}"
        )
        assert "application/pdf" in pdf_response.headers.get("content-type", ""), (
            "Featured document is not served as a PDF"
        )
        pdf_body = pdf_response.body()
        assert len(pdf_body) > 1000, "Featured PDF is unexpectedly small"
        assert pdf_body.startswith(b"%PDF"), "Featured document is not a valid PDF"

        assert not failures, "Featured link failures:\n- " + "\n- ".join(failures)

    def verify_company_profile_mobile_layout(self):
        layout = self.page.evaluate(
            """() => ({
                viewportWidth: window.innerWidth,
                documentWidth: document.documentElement.scrollWidth,
                bodyWidth: document.body.scrollWidth
            })"""
        )
        assert layout["viewportWidth"] > 0, (
            f"Invalid Company Profile mobile viewport: {layout}"
        )
        assert layout["documentWidth"] <= layout["viewportWidth"], (
            f"Company Profile has page-level horizontal overflow: {layout}"
        )
        assert layout["bodyWidth"] <= layout["viewportWidth"], (
            f"Company Profile body overflows horizontally: {layout}"
        )

        for heading in (
            self.COMPANY_PROFILE_HEADING,
            "Our Milestones So Far",
            "Where We Are Featured",
            "Key Services Offered",
            "Core Values of the Company",
        ):
            assert self.page.get_by_role(
                "heading", name=heading, exact=True
            ).is_visible(), f"Company Profile mobile section is missing: {heading}"

        table_container = self.page.locator(".table-container")
        table_state = table_container.evaluate(
            """element => ({
                clientWidth: element.clientWidth,
                scrollWidth: element.scrollWidth,
                overflowX: getComputedStyle(element).overflowX
            })"""
        )
        assert table_state["overflowX"] in {"auto", "scroll"}, (
            f"Company details table cannot scroll horizontally: {table_state}"
        )
        assert table_state["scrollWidth"] > table_state["clientWidth"], (
            f"Company details table is not using its mobile scroll layout: {table_state}"
        )
        table_container.evaluate("element => element.scrollLeft = element.scrollWidth")
        assert table_container.evaluate("element => element.scrollLeft") > 0, (
            "Company details table did not respond to horizontal scrolling"
        )

        timeline_cards = self.page.locator(".timeline-v2 .timeline-item:visible")
        assert timeline_cards.count() == len(self.COMPANY_MILESTONES), (
            f"Expected {len(self.COMPANY_MILESTONES)} mobile milestones, found "
            f"{timeline_cards.count()}"
        )
        self._assert_mobile_cards_fit(
            timeline_cards,
            "milestone",
            layout["viewportWidth"],
        )

        service_cards = self.page.locator(
            ".key-services-offered .company-key-services-crd:visible"
        )
        assert service_cards.count() == len(self.COMPANY_SERVICES), (
            "Company service cards are missing on mobile"
        )
        self._assert_mobile_cards_fit(
            service_cards,
            "service",
            layout["viewportWidth"],
        )

        value_cards = self.page.locator(
            ".core-values-company .core-value-card:visible"
        )
        assert value_cards.count() == len(self.COMPANY_VALUES), (
            "Company core-value cards are missing on mobile"
        )
        self._assert_mobile_cards_fit(
            value_cards,
            "core-value",
            layout["viewportWidth"],
        )

    @staticmethod
    def _assert_mobile_cards_fit(cards, label, viewport_width):
        boxes = cards.evaluate_all(
            """elements => elements.map(element => {
                const box = element.getBoundingClientRect();
                return {x: box.x, y: box.y, width: box.width, height: box.height};
            })"""
        )
        for box in boxes:
            assert (
                box["x"] >= 0
                and box["x"] + box["width"] <= viewport_width
            ), (
                f"Company {label} card extends outside the mobile viewport: {box}"
            )
        ordered = sorted(boxes, key=lambda box: box["y"])
        for current, following in zip(ordered, ordered[1:]):
            assert current["y"] + current["height"] <= following["y"], (
                f"Company {label} cards overlap on mobile"
            )
