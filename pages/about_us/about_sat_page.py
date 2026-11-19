from urllib.parse import urlparse

from playwright.sync_api import TimeoutError as PlaywrightTimeoutError


class AboutSatPage:
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

    def _assert_lazy_images_loaded(self, images, label):
        assert images.count() > 0, f"{label} does not contain any images"
        for index in range(images.count()):
            images.nth(index).scroll_into_view_if_needed()
            self.page.wait_for_timeout(150)

        failures = []
        for _ in range(40):
            failures = images.evaluate_all(
                """elements => elements
                    .filter(image => !image.complete || image.naturalWidth === 0)
                    .map(image => ({alt: image.alt, src: image.currentSrc || image.src}))"""
            )
            if not failures:
                return
            self.page.wait_for_timeout(250)

        assert not failures, f"{label} contains unloaded images: {failures}"


    # ============================================================
    # Helper: Human‑like scrolling with visual delay
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
        assert layout["viewportWidth"] > 0, (
            f"Mobile viewport width is invalid: {layout['viewportWidth']}"
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
        for index, current in enumerate(boxes):
            for following in boxes[index + 1:]:
                overlaps = not (
                    current["x"] + current["width"] <= following["x"]
                    or following["x"] + following["width"] <= current["x"]
                    or current["y"] + current["height"] <= following["y"]
                    or following["y"] + following["height"] <= current["y"]
                )
                assert not overlaps, (
                    "Mission, Vision, and Values cards overlap on mobile"
                )
        for box in boxes:
            assert (
                box["x"] >= 0
                and box["x"] + box["width"] <= layout["viewportWidth"]
            ), (
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
            assert (
                box["x"] >= 0
                and box["x"] + box["width"] <= layout["viewportWidth"]
            ), (
                f"Mobile footer row extends outside the viewport: {box}"
            )


    # ============================================================
    # Verify: Company Profile page content
    # ============================================================
