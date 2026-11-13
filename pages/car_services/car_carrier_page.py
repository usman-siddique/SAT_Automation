"""Page object for the SAT Car Carrier Service."""

from urllib.parse import urlparse


class CarCarrierPage:
    DELIVERY_OPTIONS = ["Single Car Trailer", "Car Carrier Service"]
    DELIVERY_GUIDANCE = [
        "shipped individually",
        "multiple vehicles to be transported simultaneously",
    ]

    BENEFITS = [
        "Maximum Security",
        "Peace of Mind",
        "Timely Delivery",
        "Dedicated Attention",
    ]

    PROCESS_STEPS = [
        "1. Select Delivery Option",
        "2. Connect With Sales Team",
        "3. Receive Your Vehicle",
    ]
    PROCESS_GUIDANCE = [
        "single-car trailer or the car carrier service",
        "details on how your vehicle will get transported",
        "Receive your car at your doorstep",
    ]

    def __init__(self, page):
        self.page = page

    @staticmethod
    def _clean(text):
        return " ".join(text.split())

    @staticmethod
    def _assert_image_loaded(image, description):
        assert image.evaluate(
            "element => element.complete && element.naturalWidth > 0"
        ), f"{description} failed to load."

    def verify_overview(self):
        heading_text = (
            "Get your vehicle delivered to your doorstep with our "
            "Car Carrier Service"
        )
        heading = self.page.get_by_role(
            "heading", name=heading_text, exact=True
        )
        heading.wait_for(state="visible")
        banner = self.page.locator("img.ccb__bg")
        banner.wait_for(state="visible")
        self._assert_image_loaded(banner, "Car Carrier hero banner")

        body_text = self._clean(self.page.locator("body").inner_text())
        assert all(
            phrase.lower() in body_text.lower()
            for phrase in (
                "efficient and trouble-free car delivery",
                "special care for your vehicle",
                "economic solution for transportation",
                "transported effectively and safely",
                "preferred destination",
            )
        )
        return {
            "path": urlparse(self.page.url).path,
            "heading": self._clean(heading.inner_text()),
        }

    def verify_delivery_options(self):
        heading = self.page.get_by_role(
            "heading", name="Delivery Options", exact=True
        )
        heading.scroll_into_view_if_needed()
        cards = self.page.locator(".carrrier-policy-card")
        assert cards.count() == 2

        titles = []
        descriptions = []
        for index in range(cards.count()):
            card = cards.nth(index)
            titles.append(
                self._clean(
                    card.locator(
                        ".carrrier-policy-type-card-hdr"
                    ).inner_text()
                )
            )
            descriptions.append(
                self._clean(
                    card.locator(
                        ".carrier-utilize-body-hdr"
                    ).inner_text()
                )
            )
            self._assert_image_loaded(
                card.locator("img.carrier-card-img"),
                f"Delivery option image {index + 1}",
            )

        assert titles == self.DELIVERY_OPTIONS
        assert all(
            guidance.lower() in description.lower()
            for guidance, description in zip(
                self.DELIVERY_GUIDANCE, descriptions
            )
        )
        return titles

    def verify_benefits(self):
        heading = self.page.get_by_role(
            "heading", name="Benefits of Our Carrier Service", exact=True
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
            name="Steps to Utilize Our Car Carrier Service",
            exact=True,
        )
        heading.scroll_into_view_if_needed()
        cards = self.page.locator(".steps-utilize-card")
        assert cards.count() == 3

        steps = []
        descriptions = []
        for index in range(cards.count()):
            card = cards.nth(index)
            steps.append(
                self._clean(
                    card.locator(".steps-utilize-hdr").inner_text()
                )
            )
            descriptions.append(
                self._clean(
                    card.locator(".steps-utilize-para").inner_text()
                )
            )
            self._assert_image_loaded(
                card.locator("img.carrier-policy-card-icons"),
                f"Car Carrier process icon {index + 1}",
            )

        assert steps == self.PROCESS_STEPS
        assert all(
            guidance.lower() in description.lower()
            for guidance, description in zip(
                self.PROCESS_GUIDANCE, descriptions
            )
        )
        return steps
