import re
from urllib.parse import urlparse


class CustomerReviewsPage:
    PATH = "/testimonials"
    DESKTOP_HEADING = re.compile(r"Customer Reviews \((\d+) Results\)")
    MOBILE_HEADING = "Customer Reviews"

    def __init__(self, page):
        self.page = page

    def _desktop_review_cards(self):
        return self.page.locator(".cards-reviews .review-card:visible")

    def _mobile_review_cards(self):
        return self.page.locator(".mob-review-card:visible")

    def _result_count(self):
        heading = self.page.locator("h1.title-page:visible").inner_text().strip()
        match = self.DESKTOP_HEADING.fullmatch(heading)
        assert match, f"Customer Reviews result heading is invalid: {heading}"
        return int(match.group(1))

    def _submit_desktop_filters(self):
        with self.page.expect_navigation(
            wait_until="domcontentloaded",
            timeout=60000,
        ):
            self.page.locator("#submitTestimonial").click()
        self.page.locator("h1.title-page:visible").wait_for(state="visible")

    def _select_visible_dropdown_option(self, container_id, option_text):
        container = self.page.locator(container_id)
        container.wait_for(state="visible")
        container.click()
        option = self.page.locator("li.select2-results__option:visible").filter(
            has_text=option_text
        )
        option.wait_for(state="visible")
        option.click()

    def _check_internal_destination(self, href, label):
        response = self.page.request.get(
            href,
            timeout=15000,
            fail_on_status_code=False,
            max_redirects=3,
        )
        assert response.status < 400, (
            f"{label} returned HTTP {response.status}: {href}"
        )
        requested = urlparse(href).path.rstrip("/") or "/"
        final = urlparse(response.url).path.rstrip("/") or "/"
        assert final == requested, (
            f"{label} redirected unexpectedly: {href} -> {response.url}"
        )

    def go_to_customer_reviews(self):
        menu = self.page.locator("p.cnm-cls:has-text('About Us')").locator("..")
        menu.hover()
        link = menu.locator(".dropdown_content_header").get_by_role(
            "link",
            name="Customer Reviews",
            exact=True,
        )
        link.wait_for(state="visible")
        link.click()
        self.page.wait_for_url("**/testimonials", wait_until="domcontentloaded")
        self.page.wait_for_load_state("load")
        self.page.locator("h1.title-page:visible").wait_for(state="visible")
        self.page.locator("#select2-make-container").wait_for(state="visible")
        self.page.wait_for_timeout(2000)
        assert urlparse(self.page.url).path.rstrip("/") == self.PATH

    def go_to_customer_reviews_mobile(self):
        toggle = self.page.locator(
            "#menu_logo_mobile span[data-bs-target='#sidebarmobile']"
        )
        toggle.wait_for(state="visible")
        toggle.click()

        main_menu = self.page.locator("#sidebarmobile")
        main_menu.locator("a.main-items-sidebar-content").filter(
            has_text="Customer Reviews"
        ).click()

        reviews_menu = self.page.locator("#offcanvascarreviews")
        link = reviews_menu.get_by_role(
            "link",
            name="Customer Reviews",
            exact=True,
        )
        link.wait_for(state="visible")
        link.click()

        self.page.wait_for_url("**/testimonials", wait_until="domcontentloaded")
        self.page.get_by_role(
            "heading",
            name=self.MOBILE_HEADING,
            exact=True,
        ).wait_for(state="visible")

    def verify_filter_controls_reviews_and_celebrity_links(self):
        country = self.page.locator("select.testimonial_country")
        make = self.page.locator("#make")
        model = self.page.locator("#model")
        stars = self.page.locator("#star")
        search = self.page.locator("#submitTestimonial")

        assert country.count() == 1, "Customer Reviews country filter is missing"
        assert make.count() == 1, "Customer Reviews make filter is missing"
        assert model.count() == 1, "Customer Reviews model filter is missing"
        assert stars.count() == 1, "Customer Reviews star filter is missing"
        assert search.is_visible(), "Customer Reviews Search button is missing"
        assert country.locator("option").count() > 200, (
            "Customer Reviews country list is incomplete"
        )
        assert make.locator("option").count() > 10, (
            "Customer Reviews make list is incomplete"
        )
        assert stars.locator("option").all_inner_texts() == [
            "Search by stars",
            "1",
            "2",
            "3",
            "4",
            "5",
        ], "Customer Reviews star choices are incorrect"

        reviews = self._desktop_review_cards()
        assert reviews.count() > 0, "Customer Reviews did not display any reviews"
        for index in range(reviews.count()):
            card = reviews.nth(index)
            star_count = card.locator("img.yellow-star").count()
            assert 1 <= star_count <= 5, (
                f"Review {index + 1} has an invalid star rating: {star_count}"
            )
            assert card.locator(".reviewer-name").inner_text().strip(), (
                f"Review {index + 1} has no reviewer name"
            )
            assert "Review on" in card.locator(".date-created").inner_text(), (
                f"Review {index + 1} has no review date or vehicle metadata"
            )

        celebrity = self.page.get_by_role(
            "heading",
            name="Celebrity Reviews",
            exact=True,
        ).locator("xpath=ancestor::section[1]")
        slides = celebrity.locator(".reel--card-item:not(.slick-cloned)")
        assert slides.count() >= 2, "Celebrity Reviews carousel has too few slides"

        video_links = slides.locator("a.reel--icon")
        destinations = set(video_links.evaluate_all(
            "elements => elements.map(element => element.href)"
        ))
        assert destinations, "Celebrity Reviews carousel has no video links"
        for href in destinations:
            parsed = urlparse(href)
            assert parsed.path.startswith("/videos/celebrity-features"), (
                f"Celebrity review has an unexpected destination: {href}"
            )
            self._check_internal_destination(href, "Celebrity review link")

        track = celebrity.locator(".slick-track")
        initial_transform = track.evaluate("element => element.style.transform")
        next_button = celebrity.get_by_role("button", name="Next", exact=True)
        assert next_button.is_enabled(), "Celebrity Reviews Next button is disabled"
        next_button.click()
        self.page.wait_for_function(
            """initial => document.querySelector(
                '.reels-youtube .slick-track'
            )?.style.transform !== initial""",
            arg=initial_transform,
        )

        view_more = celebrity.get_by_role("link", name="View More", exact=True)
        assert view_more.get_attribute("href") == "https://www.youtube.com/@satjapan/shorts", (
            "Celebrity Reviews View More link has the wrong destination"
        )

    def verify_country_filters_and_empty_state(self):
        country_filter = self.page.locator("select.testimonial_country")

        for country in ("Pakistan", "United States of America"):
            country_filter.select_option(label=country)
            self._submit_desktop_filters()

            cards = self._desktop_review_cards()
            flags = cards.locator(".country-flag")
            result_count = self._result_count()
            assert result_count > 0, f"{country} filter returned no reviews"
            assert cards.count() == result_count, (
                f"{country} result count does not match the displayed reviews"
            )
            assert flags.count() == result_count, (
                f"{country} results contain reviews without a country"
            )
            actual_countries = [
                " ".join(text.split()) for text in flags.all_inner_texts()
            ]
            assert set(actual_countries) == {country}, (
                f"{country} filter returned other countries: {actual_countries}"
            )

        country_filter.select_option(label="Andorra")
        self._submit_desktop_filters()
        assert self._result_count() == 0, "Andorra should have zero review results"
        assert self._desktop_review_cards().count() == 0, (
            "Reviews remained visible for an empty country filter"
        )
        assert self.page.get_by_text(
            "There are no reviews against these filters",
            exact=True,
        ).is_visible(), "Customer Reviews empty-state message is missing"

        country_filter.select_option("")
        self._submit_desktop_filters()
        assert urlparse(self.page.url).path.rstrip("/") == self.PATH
        assert country_filter.locator("option:checked").inner_text() == "Country"
        assert self._desktop_review_cards().count() > 0, (
            "Clearing the country filter did not restore reviews"
        )

    def verify_make_model_and_star_filters(self):
        make = self.page.locator("#make")
        model = self.page.locator("#model")
        stars = self.page.locator("#star")

        self._select_visible_dropdown_option("#select2-make-container", "Toyota")
        self.page.wait_for_function(
            "() => document.querySelector('#model')?.options.length > 1"
        )
        model_options = model.locator("option").all_inner_texts()
        assert "ALLION" in model_options, (
            "Toyota selection did not load the ALLION model"
        )

        self._select_visible_dropdown_option("#select2-model-container", "ALLION")
        self._select_visible_dropdown_option("#select2-star-container", "4")
        assert make.locator("option:checked").inner_text() == "Toyota"
        assert model.locator("option:checked").inner_text() == "ALLION"
        assert stars.locator("option:checked").inner_text() == "4"
        self._submit_desktop_filters()

        assert "/mk_toyota/md_allion/star_4" in urlparse(self.page.url).path, (
            f"Combined filter generated the wrong URL: {self.page.url}"
        )
        cards = self._desktop_review_cards()
        result_count = self._result_count()
        assert result_count > 0, "Toyota ALLION 4-star filter returned no reviews"
        assert cards.count() == result_count

        for index in range(cards.count()):
            card = cards.nth(index)
            assert "Review on Toyota ALLION" in " ".join(card.inner_text().split()), (
                f"Combined filter returned a non-Toyota ALLION review at row {index + 1}"
            )
            assert card.locator("img.yellow-star").count() == 4, (
                f"Combined filter returned a non-4-star review at row {index + 1}"
            )

    def verify_mobile_country_filter_reset_and_layout(self):
        for label in ("Country", "Make", "Model", "Stars"):
            assert self.page.get_by_role(
                "button",
                name=label,
                exact=True,
            ).is_visible(), f"Mobile {label} filter is missing"

        assert self._mobile_review_cards().count() > 0, (
            "Mobile Customer Reviews did not display reviews"
        )

        self.page.locator("#MakeItem").click()
        picker = self.page.locator("#offcanvasBottommake")
        picker.wait_for(state="visible")
        search = picker.get_by_placeholder("Search by Country")
        search.fill("Pakistan")
        pakistan = picker.locator("li.list-group-item").filter(
            has_text="Pakistan"
        )
        assert pakistan.count() == 1, (
            "Mobile country search did not narrow the list to Pakistan"
        )
        pakistan.click()
        assert self.page.locator("#MakeItem").inner_text().strip() == "Pakistan"

        with self.page.expect_navigation(
            wait_until="domcontentloaded",
            timeout=60000,
        ):
            self.page.locator("#search_card_mobile button.mobile-card-btn").filter(
                has_text="Search"
            ).click()

        assert "/testimonials/loc_pakistan" in urlparse(self.page.url).path
        cards = self._mobile_review_cards()
        assert cards.count() > 0, "Mobile Pakistan filter returned no reviews"
        flags = cards.locator("img.review-testi-detl-flg")
        assert flags.count() == cards.count(), (
            "A filtered mobile review has no country flag"
        )
        assert set(flags.evaluate_all(
            "elements => elements.map(element => element.alt)"
        )) == {"Pakistan"}, "Mobile Pakistan filter returned another country"

        reset = self.page.get_by_text("Reset Search", exact=True)
        with self.page.expect_navigation(
            wait_until="domcontentloaded",
            timeout=60000,
        ):
            reset.click()
        assert urlparse(self.page.url).path.rstrip("/") == self.PATH
        assert self.page.locator("#MakeItem").inner_text().strip() == "Country"
        assert self._mobile_review_cards().count() > 0, (
            "Mobile Reset Search did not restore reviews"
        )
