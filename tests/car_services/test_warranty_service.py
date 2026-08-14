import allure
import pytest

from pages.car_services.car_services_page import CarServicesPage
from pages.car_services.warranty_service_page import WarrantyServicePage


@pytest.fixture
def warranty(page_no_login):
    CarServicesPage(page_no_login).go_to_warranty_service()
    return WarrantyServicePage(page_no_login)


def test_warranty_service_page_content(warranty):
    with allure.step("Verify Warranty Service main heading"):
        assert warranty.get_main_heading() == "SAT Japan Warranty"

    with allure.step("Verify warranty-coverage heading"):
        assert (
            warranty.get_coverage_heading()
            == "What Does the SAT Japan Warranty Cover?"
        )

    with allure.step("Verify all warranty claim-process headings"):
        assert warranty.get_claim_process_headings() == [
            "How to Report an Issue",
            "Step 1: Contact Us Within 48 Hours",
            "Step 2: We Assess Your Claim",
            "Step 3: Repair Begins",
            "Step 4: You Get Reimbursed",
        ]

    with allure.step("Verify warranty FAQ heading"):
        assert warranty.get_faq_heading() == "Frequently Asked Questions"
