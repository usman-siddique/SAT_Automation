"""Page object for the SAT Pre-Export Inspection service."""

from pathlib import Path
from urllib.parse import urlparse

from pages.car_services.image_assertions import assert_image_loaded


class PreExportInspectionPage:
    COVERAGE_ITEMS = [
        "Engine Condition",
        "Engine Health",
        "Odometer Tampering",
        "Accidental History",
        "Interior Evaluation",
    ]
    BENEFITS = [
        "Consumer Protection",
        "Quality Assurance",
        "Fraud Prevention",
        "Comfort and Security",
    ]
    PROCESS_STEPS = [
        "1. Place Your Order",
        "2. Connect With Our Sales Team",
        "3. Get Your Inspection Report",
        "4. Receive Your Inspected Vehicle",
    ]
    PROCESS_GUIDANCE = [
        "Japanese used auto collection",
        "preferences of what you want to get inspected",
        "thorough inspection report",
        "decided destination port",
    ]

    def __init__(self, page, download_dir):
        self.page = page
        self.download_dir = Path(download_dir)

    @staticmethod
    def _clean(text):
        return " ".join(text.split())

    @staticmethod
    def _assert_image_loaded(image, description):
        assert_image_loaded(image, description)

    def verify_overview_and_refund_policy(self):
        hero_heading = self.page.get_by_role(
            "heading",
            name="Seal The Deal With Pre-Export Inspection",
            exact=True,
        )
        hero_heading.wait_for(state="visible")

        hero_image = self.page.locator("img.peb__bg")
        hero_image.wait_for(state="visible")
        self._assert_image_loaded(hero_image, "Pre-Export Inspection banner")

        refund_heading = self.page.get_by_role(
            "heading", name="Easy Refund Policy", exact=True
        )
        refund_heading.scroll_into_view_if_needed()
        refund_heading.wait_for(state="visible")

        body_text = self._clean(self.page.locator("body").inner_text())
        required_details = (
            "mechanical, electronic, and cosmetic condition",
            "mechanical, electronic, interior, and more",
            "compensated for the cost of all necessary repairs",
            "up to the full amount of the damages",
        )
        missing_details = [
            detail
            for detail in required_details
            if detail.lower() not in body_text.lower()
        ]
        assert not missing_details, (
            "Pre-Export Inspection is missing required visible content: "
            + "; ".join(missing_details)
        )

        report_link = self.page.locator("a[download][href$='.pdf']")
        report_link.wait_for(state="visible")
        report_url = report_link.get_attribute("href") or ""
        assert urlparse(report_url).path.lower().endswith(".pdf")

        return {
            "path": urlparse(self.page.url).path,
            "heading": self._clean(hero_heading.inner_text()),
            "refund_heading": self._clean(refund_heading.inner_text()),
            "report_url": report_url,
        }

    def verify_coverage_and_benefits(self):
        coverage_heading = self.page.get_by_role(
            "heading", name="What Our Service Covers", exact=True
        )
        coverage_heading.scroll_into_view_if_needed()

        coverage_cards = self.page.locator(".pre-card-cover")
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
                card.locator("img.pre-export-img"),
                f"Inspection coverage icon {index + 1}",
            )
        assert coverage_items == self.COVERAGE_ITEMS

        benefits_heading = self.page.get_by_role(
            "heading",
            name="Benefits of Our Pre-export Inspection",
            exact=True,
        )
        benefits_heading.scroll_into_view_if_needed()
        benefit_cards = self.page.locator(".pre-export-ins-card")
        assert benefit_cards.count() == len(self.BENEFITS)
        benefits = [
            self._clean(
                benefit_cards.nth(index)
                .locator(".pre-export-crd-hdr")
                .inner_text()
            )
            for index in range(benefit_cards.count())
        ]
        assert benefits == self.BENEFITS
        return {"coverage": coverage_items, "benefits": benefits}

    def verify_process_steps(self):
        heading = self.page.get_by_role(
            "heading",
            name="Steps to Utilize Our Inspection Service",
            exact=True,
        )
        heading.scroll_into_view_if_needed()

        cards = self.page.locator(".pre-export-service-crd")
        assert cards.count() == len(self.PROCESS_STEPS)
        steps = []
        descriptions = []
        for index in range(cards.count()):
            card = cards.nth(index)
            steps.append(
                self._clean(card.locator(".pre-export-ser-hdr").inner_text())
            )
            descriptions.append(
                self._clean(card.locator(".pre-export-bdy-para").inner_text())
            )
            self._assert_image_loaded(
                card.locator("img.services-crd-icons"),
                f"Inspection process icon {index + 1}",
            )

        assert steps == self.PROCESS_STEPS
        assert all(
            guidance.lower() in description.lower()
            for guidance, description in zip(
                self.PROCESS_GUIDANCE, descriptions
            )
        )
        return steps

    def download_sample_report(self):
        report_link = self.page.locator("a[download][href$='.pdf']")
        report_link.scroll_into_view_if_needed()

        with self.page.expect_download() as download_info:
            report_link.click()
        download = download_info.value

        assert download.suggested_filename.lower().endswith(".pdf")
        download_path = self.download_dir / download.suggested_filename
        download.save_as(str(download_path))

        assert download_path.exists(), "Downloaded report was not saved."
        assert download_path.stat().st_size > 1000, (
            "Downloaded inspection report is unexpectedly small."
        )
        with download_path.open("rb") as report:
            assert report.read(4) == b"%PDF", (
                "Downloaded inspection report is not a valid PDF file."
            )

        return {
            "filename": download.suggested_filename,
            "size": download_path.stat().st_size,
            "path": str(download_path),
        }
