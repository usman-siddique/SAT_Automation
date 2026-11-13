"""Page object for the SAT Finance Service."""

from urllib.parse import urlparse


class FinanceServicePage:
    PROCESS_STEPS = [
        "Select Your Vehicle",
        "Contact Sales",
        "Finalize Payment Method",
        "Enjoy Your Ride",
    ]

    PROCESS_GUIDANCE = [
        "wide inventory of Japanese used cars",
        "most suitable monthly payment plan",
        "Credit/Debit card, PayPal, or Bank Transfer",
        "remaining balance in installments",
    ]

    BENEFITS = [
        "Financial Flexibility",
        "Immediate Ownership",
        "Access Better Models",
        "Expert Assistance",
    ]

    BENEFIT_GUIDANCE = [
        "reduce financial strain",
        "without any further delay",
        "higher-end models",
        "premium support",
    ]

    def __init__(self, page):
        self.page = page

    @staticmethod
    def _clean(text):
        return " ".join(text.split())

    def verify_overview(self):
        hero_heading = self.page.get_by_role(
            "heading",
            name="Enjoy flexible payment options with our Finance Service",
            exact=True,
        )
        hero_heading.wait_for(state="visible")
        main_heading = self.page.get_by_role(
            "heading", name="Pay With Easy Installments", exact=True
        )
        main_heading.wait_for(state="visible")

        banner = self.page.locator("img.fb__bg")
        banner.wait_for(state="visible")
        assert banner.evaluate(
            "image => image.complete && image.naturalWidth > 0"
        ), "Finance Service banner failed to load."

        body_text = self._clean(self.page.locator("body").inner_text())
        assert "buying a car is not a small investment" in body_text
        assert "payment flexibility" in body_text

        return {
            "path": urlparse(self.page.url).path,
            "hero_heading": hero_heading.inner_text().strip(),
            "main_heading": main_heading.inner_text().strip(),
            "banner_alt": banner.get_attribute("alt") or "",
        }

    def verify_video_embed(self):
        video = self.page.locator("iframe[title='YouTube video player']")
        video.scroll_into_view_if_needed()
        video.wait_for(state="visible")
        source = video.get_attribute("src") or ""
        assert any(
            host in source
            for host in (
                "youtube.com/embed/",
                "youtube-nocookie.com/embed/",
            )
        ), f"Unexpected Finance video embed URL: {source}"
        assert video.get_attribute("allowfullscreen") is not None
        return source

    def verify_finance_process(self):
        all_cards = self.page.locator(".finance-services-card-work")
        assert all_cards.count() == 8
        process_cards = [all_cards.nth(index) for index in range(4)]

        headings = []
        descriptions = []
        for card in process_cards:
            headings.append(
                self._clean(
                    card.locator(".finance-services-hdr").inner_text()
                )
            )
            descriptions.append(
                self._clean(
                    card.locator(".finance-services-para").inner_text()
                )
            )
            assert card.locator("img").evaluate(
                "image => image.complete && image.naturalWidth > 0"
            )

        assert headings == self.PROCESS_STEPS
        assert all(
            guidance.lower() in description.lower()
            for guidance, description in zip(
                self.PROCESS_GUIDANCE, descriptions
            )
        )

        body_text = self._clean(self.page.locator("body").inner_text())
        assert "monthly installments for 24 months" in body_text
        assert "equal flexible installments" in body_text
        return headings

    def verify_finance_benefits(self):
        heading = self.page.get_by_role(
            "heading", name="Why Choose Our Finance Service", exact=True
        )
        heading.scroll_into_view_if_needed()
        all_cards = self.page.locator(".finance-services-card-work")
        assert all_cards.count() == 8
        benefit_cards = [all_cards.nth(index) for index in range(4, 8)]

        headings = []
        descriptions = []
        for card in benefit_cards:
            headings.append(
                self._clean(
                    card.locator(".finance-services-hdr").inner_text()
                )
            )
            descriptions.append(
                self._clean(
                    card.locator(".finance-services-para").inner_text()
                )
            )
            assert card.locator("img").evaluate(
                "image => image.complete && image.naturalWidth > 0"
            )

        assert headings == self.BENEFITS
        assert all(
            guidance.lower() in description.lower()
            for guidance, description in zip(
                self.BENEFIT_GUIDANCE, descriptions
            )
        )
        return headings
