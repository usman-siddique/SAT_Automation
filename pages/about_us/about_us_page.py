# ============================================================
# pages/about_us/about_us_page.py
# Handles About Us hover menu navigation and
# static page verifications for:
#   - About SAT
#   - Company Profile
#   - Why Choose SAT
#   - Privacy Policy
#   - Terms and Conditions
#   - Shipping Agents
# ============================================================

import sys
import os
from datetime import date
from urllib.parse import urlparse

from playwright.sync_api import TimeoutError as PlaywrightTimeoutError

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class AboutUsPage:
    ABOUT_SAT_HERO = "Simplifying Car Purchasing Globally"
    ABOUT_SAT_SECTIONS = (
        "Our Mission, Vision, and Values",
        "SAT Japan at a Glance",
        "Where We Are Featured",
        "Redefining Vehicle Access Globally",
        "Our Milestones",
    )
    ABOUT_SAT_MILESTONES = {
        "200+ Countries": "We have a global presence in 200+ countries",
        "1M+ Cars Sold": "We have sold over 1 million cars since 2002",
        "100,000+ Cars": "We have over 100,000 cars in our inventory",
        "1000+ Daily Inquiries": "Our sales team connects with over 1000 people daily",
        "10 Local Offices": "We have 10 local offices across the globe",
        "500+ Employees": "We have 500+ employees who work together",
    }
    ABOUT_SAT_CAROUSEL_TITLES = (
        "Quality that moves communities",
        "Empowering global mobility",
        "People at the heart of every decision",
        "Building opportunities across borders",
    )
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


    # ============================================================
    # Helper: Human‑like scrolling with visual delay
    # ============================================================

    def _human_scroll(self, steps=6, step_distance=350, pause_between=0.8):
        """
        Scrolls down the page in multiple small steps with pauses,
        simulating human behaviour. Then scrolls to the bottom.
        """
        for _ in range(steps):
            self.page.mouse.wheel(0, step_distance)
            self.page.wait_for_timeout(pause_between * 1000)
        # Final scroll to bottom
        self.page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        self.page.wait_for_load_state("networkidle")
        # Extra pause to see the bottom
        self.page.wait_for_timeout(500)


    # ============================================================
    # Helper: Hover About Us menu and click a sub-link
    # ============================================================

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

    def go_to_about_sat(self):
        self._navigate_to(
            "About SAT",
            "h1:has-text('Simplifying Car Purchasing Globally')",
        )
        assert urlparse(self.page.url).path.rstrip("/") == "/about-us", (
            f"About SAT navigation opened the wrong URL: {self.page.url}"
        )

    def go_to_about_sat_mobile(self):
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
        about_sat = about_menu.get_by_role("link", name="About SAT", exact=True)
        about_sat.wait_for(state="visible")
        about_sat.click()

        self.page.wait_for_url("**/about-us", wait_until="domcontentloaded")
        self.page.get_by_role(
            "heading", name=self.ABOUT_SAT_HERO, exact=True
        ).wait_for(state="visible")


    # ============================================================
    # Navigation: Company Profile
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
    # Navigation: Why Choose SAT
    # ============================================================

    def go_to_why_choose_sat(self):
        self._navigate_to("Why Choose SAT", "h1.why-title")
        print("✅ Navigation to Why Choose SAT: PASS")


    # ============================================================
    # Navigation: Privacy Policy
    # ============================================================

    def go_to_privacy_policy(self):
        self._navigate_to("Privacy Policy", "section.cookies-polices-main h2.cookies-polices-comman-hdr")
        print("✅ Navigation to Privacy Policy: PASS")


    # ============================================================
    # Navigation: Terms and Conditions
    # ============================================================

    def go_to_terms_and_conditions(self):
        self._navigate_to("Terms and Conditions", "h1.term-main-hdr")
        print("✅ Navigation to Terms and Conditions: PASS")


    # ============================================================
    # Navigation: Shipping Agents
    # ============================================================

    def go_to_shipping_agents(self):
        self._navigate_to("Shipping Agents", "h1.title-shipagent")
        print("✅ Navigation to Shipping Agents: PASS")


    # ============================================================
    # Verify: About SAT page content
    # ============================================================

    def verify_about_sat(self):
        hero = self._section_with_heading(self.ABOUT_SAT_HERO)
        assert hero.get_by_role(
            "heading", name=self.ABOUT_SAT_HERO, exact=True
        ).is_visible(), "About SAT hero heading is not visible"
        assert "Operating in 200+ countries" in hero.inner_text(), (
            "About SAT hero does not explain the global service coverage"
        )

        for heading in self.ABOUT_SAT_SECTIONS:
            assert self.page.get_by_role(
                "heading", name=heading, exact=True
            ).is_visible(), f"About SAT section is missing: {heading}"

        values = self._section_with_heading("Our Mission, Vision, and Values")
        expected_values = {
            "Mission": "simplify the car sale process",
            "Vision": "simplify buying and selling cars for everyone",
            "Values": "innovation, transparency, and customer satisfaction",
        }
        for title, expected_text in expected_values.items():
            card = values.get_by_role(
                "heading", name=title, exact=True
            ).locator("xpath=..")
            assert expected_text in card.inner_text(), (
                f"{title} card does not contain its expected business message"
            )

        milestones = self._section_with_heading("Our Milestones")
        for title, expected_text in self.ABOUT_SAT_MILESTONES.items():
            milestone = milestones.get_by_role(
                "heading", name=title, exact=True
            ).locator("xpath=..")
            assert expected_text in milestone.inner_text(), (
                f"Milestone content is incomplete: {title}"
            )

    def verify_about_sat_media_and_carousel(self):
        hero = self._section_with_heading(self.ABOUT_SAT_HERO)
        values = self._section_with_heading("Our Mission, Vision, and Values")
        gallery = self._section_with_heading("SAT Japan at a Glance")
        featured = self._featured_container()
        carousel = self._section_with_heading(
            "Redefining Vehicle Access Globally"
        )

        self._assert_images_loaded(hero.locator("img"), "About SAT hero")
        self._assert_images_loaded(values.locator("img"), "Mission cards")
        self._assert_images_loaded(gallery.locator("img"), "At a Glance gallery")
        self._assert_images_loaded(featured.locator("a.item img"), "Featured logos")
        self._assert_images_loaded(carousel.locator("img"), "Vehicle access carousel")

        tracks = gallery.locator(".glance-track")
        assert tracks.count() == 2, "At a Glance should contain two animated tracks"
        initial_transforms = tracks.evaluate_all(
            "elements => elements.map(element => getComputedStyle(element).transform)"
        )
        self.page.wait_for_function(
            """initial => [...document.querySelectorAll('.glance-track')]
                .some((track, index) =>
                    getComputedStyle(track).transform !== initial[index])""",
            arg=initial_transforms,
            timeout=5000,
        )

        featured_links = featured.locator("a.item")
        assert featured_links.count() == self.FEATURE_LINK_COUNT, (
            f"Expected {self.FEATURE_LINK_COUNT} featured links, found "
            f"{featured_links.count()}"
        )

        carousel_text = carousel.inner_text()
        for title in self.ABOUT_SAT_CAROUSEL_TITLES:
            assert title in carousel_text, f"Carousel card is missing: {title}"

        dots = carousel.locator("[role='tab']")
        assert dots.count() == 4, "Vehicle access carousel should have four positions"
        assert dots.nth(0).get_attribute("aria-selected") == "true", (
            "Vehicle access carousel did not start on its first position"
        )

        carousel.locator(".custom-next.redefine").click()
        self.page.wait_for_function(
            """() => document.querySelectorAll(
                "section [role='tab']"
            )[1]?.getAttribute('aria-selected') === 'true'"""
        )
        carousel.locator(".custom-prev.redefine").click()
        self.page.wait_for_function(
            """() => document.querySelectorAll(
                "section [role='tab']"
            )[0]?.getAttribute('aria-selected') === 'true'"""
        )

    def verify_about_sat_feature_links_and_pdf(self):
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

    def verify_about_sat_mobile_layout(self):
        layout = self.page.evaluate(
            """() => ({
                viewportWidth: window.innerWidth,
                documentWidth: document.documentElement.scrollWidth,
                bodyWidth: document.body.scrollWidth
            })"""
        )
        assert layout["viewportWidth"] == 390, (
            f"Unexpected mobile viewport width: {layout['viewportWidth']}"
        )
        assert layout["documentWidth"] <= layout["viewportWidth"], (
            f"Page has horizontal overflow: {layout}"
        )
        assert layout["bodyWidth"] <= layout["viewportWidth"], (
            f"Page body has horizontal overflow: {layout}"
        )

        assert self.page.locator("#navbar_mobile_header").is_visible(), (
            "Mobile navigation header is not visible"
        )
        for heading in (self.ABOUT_SAT_HERO, *self.ABOUT_SAT_SECTIONS):
            assert self.page.get_by_role(
                "heading", name=heading, exact=True
            ).is_visible(), f"Mobile section is missing: {heading}"

        values = self._section_with_heading("Our Mission, Vision, and Values")
        cards = [
            values.get_by_role("heading", name=title, exact=True).locator("xpath=..")
            for title in ("Mission", "Vision", "Values")
        ]
        boxes = [card.bounding_box() for card in cards]
        assert all(boxes), "A Mission, Vision, or Values card has no mobile layout box"
        for current, following in zip(boxes, boxes[1:]):
            assert current["y"] + current["height"] <= following["y"], (
                "Mission, Vision, and Values cards overlap on mobile"
            )
        for box in boxes:
            assert box["x"] >= 0 and box["x"] + box["width"] <= 390, (
                f"Mission card extends outside the mobile viewport: {box}"
            )

        footer_buttons = self.page.locator("button.accordion-button:visible")
        assert footer_buttons.count() >= 9, (
            "Mobile footer accordions are missing or using the desktop layout"
        )
        footer_boxes = footer_buttons.evaluate_all(
            """elements => elements.map(element => {
                const box = element.getBoundingClientRect();
                return {x: box.x, y: box.y, width: box.width, height: box.height};
            })"""
        )
        for current, following in zip(footer_boxes, footer_boxes[1:]):
            assert current["y"] + current["height"] <= following["y"], (
                "Mobile footer accordion rows overlap"
            )
        for box in footer_boxes:
            assert box["x"] >= 0 and box["x"] + box["width"] <= 390, (
                f"Mobile footer row extends outside the viewport: {box}"
            )


    # ============================================================
    # Verify: Company Profile page content
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
        self.verify_about_sat_feature_links_and_pdf()

    def verify_company_profile_mobile_layout(self):
        layout = self.page.evaluate(
            """() => ({
                viewportWidth: window.innerWidth,
                documentWidth: document.documentElement.scrollWidth,
                bodyWidth: document.body.scrollWidth
            })"""
        )
        assert layout["viewportWidth"] == 390, (
            f"Unexpected Company Profile mobile viewport: {layout}"
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
        self._assert_mobile_cards_fit(timeline_cards, "milestone")

        service_cards = self.page.locator(
            ".key-services-offered .company-key-services-crd:visible"
        )
        assert service_cards.count() == len(self.COMPANY_SERVICES), (
            "Company service cards are missing on mobile"
        )
        self._assert_mobile_cards_fit(service_cards, "service")

        value_cards = self.page.locator(
            ".core-values-company .core-value-card:visible"
        )
        assert value_cards.count() == len(self.COMPANY_VALUES), (
            "Company core-value cards are missing on mobile"
        )
        self._assert_mobile_cards_fit(value_cards, "core-value")

    @staticmethod
    def _assert_mobile_cards_fit(cards, label):
        boxes = cards.evaluate_all(
            """elements => elements.map(element => {
                const box = element.getBoundingClientRect();
                return {x: box.x, y: box.y, width: box.width, height: box.height};
            })"""
        )
        for box in boxes:
            assert box["x"] >= 0 and box["x"] + box["width"] <= 390, (
                f"Company {label} card extends outside the mobile viewport: {box}"
            )
        ordered = sorted(boxes, key=lambda box: box["y"])
        for current, following in zip(ordered, ordered[1:]):
            assert current["y"] + current["height"] <= following["y"], (
                f"Company {label} cards overlap on mobile"
            )


    # ============================================================
    # Verify: Why Choose SAT page content
    # ============================================================

    def verify_why_choose_sat(self):
        self._human_scroll(steps=5, step_distance=300, pause_between=0.8)

        self.page.locator("h1.why-title:has-text('Why Choose SAT Japan?')").wait_for(state="visible")
        self.page.wait_for_timeout(300)
        assert self.page.locator("h1.why-title:has-text('Why Choose SAT Japan?')").is_visible(), \
            "❌ Why Choose SAT heading not visible"

        assert self.page.locator("h2:has-text('Exceptional Customer Support')").is_visible(), \
            "❌ Exceptional Customer Support section not visible"

        self.page.wait_for_timeout(500)
        print("✅ Why Choose SAT content verified")


    # ============================================================
    # Verify: Privacy Policy page content
    # ============================================================

    def verify_privacy_policy(self):
        self._human_scroll(steps=6, step_distance=280, pause_between=0.8)

        main = self.page.locator("section.cookies-polices-main")
        main.locator("h2.cookies-polices-comman-hdr:has-text('Privacy Policy')").wait_for(state="visible")
        self.page.wait_for_timeout(300)
        assert main.locator("h2.cookies-polices-comman-hdr:has-text('Privacy Policy')").is_visible(), \
            "❌ Privacy Policy heading not visible"

        contact = self.page.locator("div.contact-us-section h2.cookies-polices-comman-hdr:has-text('Contact us')")
        contact.wait_for(state="visible")
        self.page.wait_for_timeout(300)
        assert contact.is_visible(), "❌ Contact us section not visible"

        self.page.wait_for_timeout(500)
        print("✅ Privacy Policy content verified")


    # ============================================================
    # Verify: Terms and Conditions page content
    # ============================================================

    def verify_terms_and_conditions(self):
        self._human_scroll(steps=5, step_distance=350, pause_between=0.8)

        self.page.locator("h1.term-main-hdr:has-text('Terms and Conditions')").wait_for(state="visible")
        self.page.wait_for_timeout(300)
        assert self.page.locator("h1.term-main-hdr:has-text('Terms and Conditions')").is_visible()

        link = self.page.locator("a:has-text('vehicle purchase agreement')")
        link.wait_for(state="visible")
        self.page.wait_for_timeout(300)
        href = link.get_attribute("href")
        assert "vehicle-sales-agreement.pdf" in href

        headless = os.getenv("HEADLESS", "false").lower() == "true"
        if not headless:
            with self.page.context.expect_page() as new_tab_info:
                link.click()
                self.page.wait_for_timeout(300)
            new_tab = new_tab_info.value
            new_tab.wait_for_url("**/vehicle-sales-agreement.pdf")
            self.page.wait_for_timeout(500)
            assert "vehicle-sales-agreement.pdf" in new_tab.url
            new_tab.close()
        else:
            print("⚠️ Headless mode: PDF link verified, but opening skipped (PDF would download)")

        self.page.wait_for_timeout(500)
        print("✅ Terms and Conditions content verified")


    # ============================================================
    # Verify: Shipping Agents page content
    # ============================================================

    def verify_shipping_agents(self):
        self._human_scroll(steps=5, step_distance=300, pause_between=0.8)

        self.page.locator("h1.title-shipagent:has-text('Explore Our International Office Map')").wait_for(state="visible")
        self.page.wait_for_timeout(300)
        assert self.page.locator("h1.title-shipagent:has-text('Explore Our International Office Map')").is_visible(), \
            "❌ Shipping Agents heading not visible"

        assert self.page.locator("img[alt='sat agent map']").is_visible(), \
            "❌ Agent map image not visible"

        filter_label = self.page.locator("span.title:has-text('Filter by country:')").first
        filter_label.wait_for(state="visible")
        self.page.wait_for_timeout(300)
        assert filter_label.is_visible(), "❌ Filter by country label not visible"

        self.page.wait_for_timeout(500)
        print("✅ Shipping Agents content verified")
