"""Page object for the SAT Customs Clearance Service."""

from urllib.parse import urlparse

from pages.car_services.image_assertions import assert_image_loaded


class CustomsClearancePage:
    BENEFITS = [
        "Comfort and Ease",
        "Expert Handling",
        "Personalized Service",
        "Peace of Mind",
    ]

    PROCESS_STEPS = [
        "1. Place Your Order",
        "2. Connect With Our Sales Team",
        "3. Documentation Handling",
        "4. Pick Up Your Vehicle",
    ]
    PROCESS_GUIDANCE = [
        "extensive inventory of Japanese used cars",
        "smooth and carefree delivery",
        "compliance with local laws",
        "predetermined destination",
    ]

    def __init__(self, page):
        self.page = page

    @staticmethod
    def _clean(text):
        return " ".join(text.split())

    @staticmethod
    def _assert_image_loaded(image, description):
        assert_image_loaded(image, description)

    def verify_overview(self):
        heading = self.page.get_by_role(
            "heading",
            name="Ensure Fast and Compliant Shipments",
            exact=True,
        )
        heading.wait_for(state="visible")
        service_heading = self.page.get_by_role(
            "heading", name="Trouble-Free Customs Clearance", exact=True
        )
        service_heading.scroll_into_view_if_needed()

        hero = self.page.locator("img.csb__bg")
        hero.wait_for(state="visible")
        self._assert_image_loaded(hero, "Customs Clearance hero banner")
        content_image = self.page.locator("img.finance-body-img")
        content_image.scroll_into_view_if_needed()
        content_image.wait_for(state="visible")
        self._assert_image_loaded(
            content_image, "Customs Clearance content image"
        )

        body_text = self._clean(self.page.locator("body").inner_text())
        required_points = (
            "local experts handle shipping and customs clearance",
            "professional local agents take care of all the paperwork",
            "entire process from the time you decide to purchase a car",
            "documentation and local requirements",
        )
        assert all(
            point.lower() in body_text.lower()
            for point in required_points
        )
        return {
            "path": urlparse(self.page.url).path,
            "heading": self._clean(heading.inner_text()),
            "service_heading": service_heading.inner_text().strip(),
        }

    def verify_benefits(self):
        heading = self.page.get_by_role(
            "heading",
            name="Why Choose Our Customs Clearance Service",
            exact=True,
        )
        heading.scroll_into_view_if_needed()
        cards = self.page.locator(".carrier-service-card")
        assert cards.count() == 4
        benefits = [
            self._clean(
                cards.nth(index).locator(
                    ".carrier-service-card-hdr"
                ).inner_text()
            )
            for index in range(cards.count())
        ]
        assert benefits == self.BENEFITS
        return benefits

    def verify_process_steps(self):
        heading = self.page.get_by_role(
            "heading",
            name="Steps to Utilize Our Customs Clearance Service",
            exact=True,
        )
        heading.scroll_into_view_if_needed()
        cards = self.page.locator(".finance-services-card")
        assert cards.count() == 4

        steps = []
        descriptions = []
        for index in range(cards.count()):
            card = cards.nth(index)
            steps.append(
                self._clean(
                    card.locator(".finance-type-card-hdr").inner_text()
                )
            )
            descriptions.append(
                self._clean(
                    card.locator(".finance-utilize-body-hdr").inner_text()
                )
            )
            self._assert_image_loaded(
                card.locator("img.finance-card-icons"),
                f"Customs Clearance step icon {index + 1}",
            )

        assert steps == self.PROCESS_STEPS
        assert all(
            guidance.lower() in description.lower()
            for guidance, description in zip(
                self.PROCESS_GUIDANCE, descriptions
            )
        )
        return steps
