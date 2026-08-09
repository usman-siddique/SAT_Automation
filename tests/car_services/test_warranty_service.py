import pytest

from pages.car_services.car_services_page import CarServicesPage
from pages.car_services.warranty_service_page import WarrantyServicePage


@pytest.fixture
def warranty(page_no_login):
    CarServicesPage(page_no_login).go_to_warranty_service()
    return WarrantyServicePage(page_no_login)


class TestWarrantyService:
    def test_main_heading(self, warranty):
        assert warranty.get_main_heading() == "SAT Japan Warranty"

    def test_coverage_heading(self, warranty):
        assert (
            warranty.get_coverage_heading()
            == "What Does the SAT Japan Warranty Cover?"
        )

    def test_claim_process(self, warranty):
        assert warranty.get_claim_process_headings() == [
            "How to Report an Issue",
            "Step 1: Contact Us Within 48 Hours",
            "Step 2: We Assess Your Claim",
            "Step 3: Repair Begins",
            "Step 4: You Get Reimbursed",
        ]

    def test_faq_heading(self, warranty):
        assert warranty.get_faq_heading() == "Frequently Asked Questions"
