"""Page object for the SAT Marine Insurance service."""

from urllib.parse import urlparse

from pages.car_services.image_assertions import assert_image_loaded


class MarineInsurancePage:
    COVERAGE_ITEMS = [
        "Comprehensive Coverage",
        "Damage Protection",
        "Real-time Tracking",
        "Claims Assistance",
    ]

    BENEFITS = [
        "Consumer Protection",
        "Quality Assurance",
        "Peace of Mind",
        "Financial Security",
    ]

    PROCESS_STEPS = [
        "1. Place Your Order",
        "2. Connect With Our Sales Team",
        "3. Track and Get Updates",
        "4. Receive Your Documentation",
    ]

    PROCESS_GUIDANCE = [
        "Japanese used auto collections",
        "choose our Marine insurance Service",
        "Track Your Order",
        "documentation and compensation",
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
            name=(
                "Get full coverage up to the cost of the vehicle with our "
                "Marine Insurance Service"
            ),
            exact=True,
        )
        heading.wait_for(state="visible")

        banner = self.page.locator("img.nsb__bg")
        banner.wait_for(state="visible")
        self._assert_image_loaded(banner, "Marine Insurance banner")

        detail_heading = self.page.get_by_role(
            "heading", name="Detail", exact=True
        )
        detail_heading.wait_for(state="visible")
        body_text = self._clean(self.page.locator("body").inner_text())
        required_promises = (
            "assure your car’s security while exporting",
            "shipment reaches you without any sort of damage",
            "guarantee to get your payment back",
            "get a new vehicle in the same range",
        )
        assert all(
            promise.lower() in body_text.lower()
            for promise in required_promises
        )

        return {
            "path": urlparse(self.page.url).path,
            "heading": self._clean(heading.inner_text()),
            "detail_heading": self._clean(detail_heading.inner_text()),
        }

    def verify_coverage_and_benefits(self):
        coverage_heading = self.page.get_by_role(
            "heading", name="What Our Service Covers", exact=True
        )
        coverage_heading.scroll_into_view_if_needed()

        coverage_cards = self.page.locator(
            ".marine-insurance-cover-main .pre-card-cover"
        )
        assert coverage_cards.count() == len(self.COVERAGE_ITEMS)
        coverage_items = []
        for index in range(coverage_cards.count()):
            card = coverage_cards.nth(index)
            coverage_items.append(
                self._clean(
                    card.locator(".inspection-services-hdr").inner_text()
                )
            )
            self._assert_image_loaded(
                card.locator("img.marine-insurance-img"),
                f"Marine Insurance coverage icon {index + 1}",
            )
        assert coverage_items == self.COVERAGE_ITEMS

        benefits_heading = self.page.get_by_role(
            "heading",
            name="Benefits of Our Marine Insurance Service",
            exact=True,
        )
        benefits_heading.scroll_into_view_if_needed()
        benefit_cards = self.page.locator(".marine-insurance-ins-card")
        assert benefit_cards.count() == len(self.BENEFITS)
        benefits = [
            self._clean(
                benefit_cards.nth(index)
                .locator(".marine-insurance-crd-hdr")
                .inner_text()
            )
            for index in range(benefit_cards.count())
        ]
        assert benefits == self.BENEFITS
        return {"coverage": coverage_items, "benefits": benefits}

    def verify_process_steps(self):
        heading = self.page.get_by_role(
            "heading",
            name="Steps to Utilize Our Marine Insurance Service",
            exact=True,
        )
        heading.scroll_into_view_if_needed()

        cards = self.page.locator(".marine-insurance-service-crd")
        assert cards.count() == len(self.PROCESS_STEPS)
        steps = []
        descriptions = []
        for index in range(cards.count()):
            card = cards.nth(index)
            steps.append(
                self._clean(
                    card.locator(".marine-insurance-ser-hdr").inner_text()
                )
            )
            descriptions.append(
                self._clean(
                    card.locator(".marine-insurance-bdy-para").inner_text()
                )
            )
            self._assert_image_loaded(
                card.locator("img.services-crd-icons"),
                f"Marine Insurance process icon {index + 1}",
            )

        assert steps == self.PROCESS_STEPS
        assert all(
            guidance.lower() in description.lower()
            for guidance, description in zip(
                self.PROCESS_GUIDANCE, descriptions
            )
        )
        return steps
