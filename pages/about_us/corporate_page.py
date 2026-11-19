from datetime import date
from urllib.parse import parse_qs, urlparse


class CorporatePage:
    CORPORATE_HERO = "日本から150以上の国へ2万台以上の車両を輸出。"
    CORPORATE_CARDS = {
        "社長メッセージ": "/ceo-vision",
        "会社概要": "/company-profile",
        "採用情報": "/careers",
        "お客様の声": "/testimonials",
        "お問い合わせ": "/inquiry-form",
    }
    CORPORATE_SECTION_HEADINGS = (
        "購入の判断に役立つ自動車トーク",
        "お客様のレビュー",
    )

    def __init__(self, page):
        self.page = page

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

    def go_to_corporate(self):
        self._navigate_to("Corporate", "h1.title")
        assert urlparse(self.page.url).path.rstrip("/") == "/corporate", (
            f"Corporate navigation opened the wrong URL: {self.page.url}"
        )

    def go_to_corporate_mobile(self):
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
        about_menu.wait_for(state="visible")
        available_links = [
            text.strip()
            for text in about_menu.get_by_role("link").all_inner_texts()
            if text.strip()
        ]
        assert "Corporate" in available_links, (
            "Corporate is missing from the mobile About Us menu. "
            f"Available links: {available_links}"
        )

        corporate = about_menu.get_by_role("link", name="Corporate", exact=True)
        corporate.click()
        self.page.wait_for_url("**/corporate", wait_until="domcontentloaded")
        self.page.get_by_role(
            "heading", name=self.CORPORATE_HERO, exact=True
        ).wait_for(state="visible")

    def open_corporate_direct(self):
        current = urlparse(self.page.url)
        origin = f"{current.scheme}://{current.netloc}"
        response = self.page.goto(
            f"{origin}/corporate",
            wait_until="domcontentloaded",
            timeout=60000,
        )
        assert response is not None, "Corporate direct navigation returned no response"
        assert response.status < 400, (
            f"Corporate direct navigation returned HTTP {response.status}"
        )
        self.page.get_by_role(
            "heading", name=self.CORPORATE_HERO, exact=True
        ).wait_for(state="visible")


    # ============================================================
    # Verify: About SAT page content
    # ============================================================

    def _internal_link_failures(self, links, label):
        page_host = (urlparse(self.page.url).hostname or "").lower()
        failures = []
        checked = set()

        for index in range(links.count()):
            href = links.nth(index).get_attribute("href")
            if not href:
                failures.append(f"{label} link {index + 1} has no destination")
                continue

            parsed = urlparse(href)
            if parsed.scheme not in {"http", "https"} or not parsed.hostname:
                failures.append(f"{label} link has an invalid URL: {href}")
                continue
            if parsed.hostname.lower() != page_host:
                failures.append(f"{label} link is unexpectedly external: {href}")
                continue
            if href in checked:
                continue
            checked.add(href)

            try:
                response = self.page.request.get(
                    href,
                    timeout=15000,
                    fail_on_status_code=False,
                    max_redirects=3,
                )
                final = urlparse(response.url)
                requested_path = parsed.path.rstrip("/") or "/"
                final_path = final.path.rstrip("/") or "/"
                if response.status >= 400:
                    failures.append(
                        f"{label} link returned HTTP {response.status}: {href}"
                    )
                elif final.hostname and final.hostname.lower() != page_host:
                    failures.append(
                        f"{label} link left the SAT site: {href} -> {response.url}"
                    )
                elif final_path != requested_path:
                    failures.append(
                        f"{label} link redirected unexpectedly: "
                        f"{href} -> {response.url}"
                    )
                elif "text/html" not in response.headers.get("content-type", ""):
                    failures.append(
                        f"{label} link did not return an HTML page: {href}"
                    )
            except Exception as error:
                error_text = str(error)
                if "Max redirect count exceeded" in error_text:
                    failures.append(f"{label} link is stuck in a redirect loop: {href}")
                else:
                    failures.append(
                        f"{label} link could not be opened: {href} ({error_text})"
                    )

        return failures

    def _assert_internal_links_reachable(self, links, label):
        failures = self._internal_link_failures(links, label)
        assert not failures, f"{label} link failures:\n- " + "\n- ".join(failures)

    @staticmethod
    def _assert_mobile_elements_fit_without_overlap(
        elements,
        label,
        viewport_width,
    ):
        boxes = elements.evaluate_all(
            """elements => elements.map(element => {
                const box = element.getBoundingClientRect();
                return {
                    x: box.x,
                    y: box.y,
                    width: box.width,
                    height: box.height
                };
            })"""
        )
        for box in boxes:
            assert (
                box["x"] >= 0
                and box["x"] + box["width"] <= viewport_width
            ), (
                f"Corporate {label} extends outside the mobile viewport: {box}"
            )

        for index, current in enumerate(boxes):
            for following in boxes[index + 1:]:
                overlaps = not (
                    current["x"] + current["width"] <= following["x"]
                    or following["x"] + following["width"] <= current["x"]
                    or current["y"] + current["height"] <= following["y"]
                    or following["y"] + following["height"] <= current["y"]
                )
                assert not overlaps, (
                    f"Corporate {label} elements overlap on mobile"
                )

    def verify_corporate_overview_cards_and_media(self):
        hero = self.page.get_by_role(
            "heading", name=self.CORPORATE_HERO, exact=True
        )
        assert hero.is_visible(), "Corporate hero message is not visible"

        for heading in self.CORPORATE_SECTION_HEADINGS:
            assert self.page.get_by_role(
                "heading", name=heading, exact=True
            ).is_visible(), f"Corporate section is missing: {heading}"

        cards = self.page.locator("a.corporate-card")
        assert cards.count() == len(self.CORPORATE_CARDS), (
            f"Expected {len(self.CORPORATE_CARDS)} Corporate cards, "
            f"found {cards.count()}"
        )

        failures = []
        for heading, expected_path in self.CORPORATE_CARDS.items():
            card = cards.filter(has=self.page.get_by_role(
                "heading", name=heading, exact=True
            ))
            if card.count() != 1:
                failures.append(
                    f"Expected one Corporate card for '{heading}', found {card.count()}"
                )
                continue
            actual_path = urlparse(card.get_attribute("href")).path.rstrip("/")
            if actual_path != expected_path:
                failures.append(
                    f"'{heading}' should open {expected_path}, found {actual_path}"
                )

        established = date(2002, 3, 16)
        today = date.today()
        company_age = today.year - established.year - (
            (today.month, today.day) < (established.month, established.day)
        )
        if f"{company_age} Years Experience" not in self.page.title():
            failures.append(
                f"Corporate title does not match the {company_age}-year company age"
            )

        self._assert_images_loaded(
            self.page.locator(".corporate--bannar img"),
            "Corporate banner",
        )
        self._assert_lazy_images_loaded(
            self.page.locator(".corporate-grid .corporate-img img:visible"),
            "Corporate navigation cards",
        )
        self._assert_internal_links_reachable(cards, "Corporate navigation card")
        assert not failures, "Corporate content failures:\n- " + "\n- ".join(failures)

    def verify_corporate_blog_and_review_links(self):
        blog_cards = self.page.locator("a.car-talks-card:visible")
        assert blog_cards.count() == 4, (
            f"Expected four desktop Corporate blog cards, found {blog_cards.count()}"
        )
        for index in range(blog_cards.count()):
            assert blog_cards.nth(index).get_by_role("heading").inner_text().strip(), (
                f"Corporate blog card {index + 1} has no article title"
            )

        more_blogs = self.page.locator(".car-talks a.view-top-seling")
        assert more_blogs.count() == 1, "Corporate View More blog link is missing"
        self._assert_lazy_images_loaded(
            blog_cards.locator("img:visible"),
            "Corporate blog cards",
        )
        link_failures = self._internal_link_failures(
            self.page.locator(".car-talks a"),
            "Corporate blog",
        )

        reviews_heading = self.page.get_by_role(
            "heading", name="お客様のレビュー", exact=True
        )
        reviews = reviews_heading.locator(
            "xpath=ancestor::div["
            "contains(concat(' ', normalize-space(@class), ' '), ' container ')][1]"
        )
        review_cards = reviews.locator("article.cr-card")
        assert review_cards.count() == 3, (
            f"Expected three Corporate review previews, found {review_cards.count()}"
        )
        for index in range(review_cards.count()):
            review = review_cards.nth(index)
            assert review.get_by_role("heading", level=3).inner_text().strip(), (
                f"Corporate review {index + 1} has no vehicle title"
            )
            review_text = " ".join(review.inner_text().split())
            assert "By " in review_text and " on " in review_text, (
                f"Corporate review {index + 1} is missing buyer or date details"
            )

        self._assert_lazy_images_loaded(
            review_cards.locator("img:visible"),
            "Corporate reviews",
        )
        internal_review_links = reviews.locator("a.cr-card__search, a.ug-viewall__link")
        assert internal_review_links.count() == 4, (
            "Corporate reviews should contain three vehicle searches and one "
            "View All link"
        )
        link_failures.extend(
            self._internal_link_failures(
                internal_review_links,
                "Corporate review",
            )
        )

        share_links = reviews.locator("a.ug-share__btn")
        assert share_links.count() == 6, (
            f"Expected six Corporate review share links, found {share_links.count()}"
        )
        share_failures = []
        for index in range(share_links.count()):
            link = share_links.nth(index)
            href = link.get_attribute("href") or ""
            parsed = urlparse(href)
            query = parse_qs(parsed.query)
            target_url = (query.get("u") or query.get("url") or [""])[0]
            target = urlparse(target_url)
            if link.get_attribute("target") != "_blank":
                share_failures.append(f"Share link does not open in a new tab: {href}")
            if parsed.hostname not in {"www.facebook.com", "twitter.com"}:
                share_failures.append(f"Unexpected share service: {href}")
            if target.path != "/testimonials" or "id" not in parse_qs(target.query):
                share_failures.append(
                    f"Share link does not target a specific SAT review: {href}"
                )
        link_failures.extend(share_failures)
        assert not link_failures, "Corporate content link failures:\n- " + "\n- ".join(
            link_failures
        )

    def verify_corporate_mobile_layout(self):
        layout = self.page.evaluate(
            """() => ({
                viewportWidth: window.innerWidth,
                documentWidth: document.documentElement.scrollWidth,
                bodyWidth: document.body.scrollWidth
            })"""
        )
        assert layout["viewportWidth"] > 0, (
            f"Invalid Corporate mobile viewport: {layout}"
        )
        assert layout["documentWidth"] <= layout["viewportWidth"], (
            f"Corporate has page-level horizontal overflow: {layout}"
        )
        assert layout["bodyWidth"] <= layout["viewportWidth"], (
            f"Corporate body overflows horizontally: {layout}"
        )
        assert self.page.locator("#navbar_mobile_header").is_visible(), (
            "Corporate mobile header is not visible"
        )

        headings = (
            self.CORPORATE_HERO,
            *self.CORPORATE_CARDS.keys(),
            *self.CORPORATE_SECTION_HEADINGS,
        )
        for heading in headings:
            assert self.page.get_by_role(
                "heading", name=heading, exact=True
            ).is_visible(), f"Corporate mobile content is missing: {heading}"

        corporate_cards = self.page.locator("a.corporate-card:visible")
        assert corporate_cards.count() == len(self.CORPORATE_CARDS), (
            "Corporate navigation cards are missing on mobile"
        )
        self._assert_mobile_elements_fit_without_overlap(
            corporate_cards,
            "navigation cards",
            layout["viewportWidth"],
        )

        blog_cards = self.page.locator("a.car-talks-card:visible")
        assert blog_cards.count() == 5, (
            f"Expected five mobile Corporate blog cards, found {blog_cards.count()}"
        )
        self._assert_mobile_elements_fit_without_overlap(
            blog_cards,
            "blog cards",
            layout["viewportWidth"],
        )

        review_cards = self.page.locator("article.cr-card:visible")
        assert review_cards.count() == 3, (
            "Corporate review previews are missing on mobile"
        )
        self._assert_mobile_elements_fit_without_overlap(
            review_cards,
            "review cards",
            layout["viewportWidth"],
        )

        self._assert_lazy_images_loaded(
            self.page.locator(
                ".corporate--bannar img:visible, "
                ".corporate-grid .corporate-img img:visible, "
                "a.car-talks-card:visible img:visible, "
                "article.cr-card:visible img:visible"
            ),
            "Corporate mobile content",
        )
