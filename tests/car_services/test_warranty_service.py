"""Business coverage for the SAT Japan Warranty page."""

import allure

from pages.car_services.car_services_page import CarServicesPage
from pages.car_services.warranty_service_page import WarrantyServicePage


def open_warranty(page):
    CarServicesPage(page).go_to_warranty_service()
    return WarrantyServicePage(page)


def test_warranty_service_content_and_claim_process(page_no_login):
    warranty = open_warranty(page_no_login)

    with allure.step("Verify page URL, main heading, and business sections"):
        contract = warranty.verify_page_contract()
        assert contract["path"] == "/sat-warranty"
        assert contract["heading"] == "SAT Japan Warranty"
        assert len(contract["sections"]) == 5

    with allure.step("Verify all coverage categories and their icons"):
        assert warranty.verify_coverage_items() == warranty.COVERAGE_ITEMS

    with allure.step("Verify FOB reimbursement limits and exclusions"):
        assert len(warranty.verify_coverage_limits()) == 4

    with allure.step("Verify every claim step and required evidence"):
        assert warranty.verify_claim_process() == warranty.CLAIM_HEADINGS

    with allure.step("Verify Warranty and Marine Insurance differences"):
        assert warranty.verify_warranty_insurance_difference()


def test_warranty_service_faq_questions_and_answers(page_no_login):
    warranty = open_warranty(page_no_login)

    with allure.step("Open all seven Warranty FAQ accordions"):
        faqs = warranty.open_visible_faqs()
        assert len(faqs["answers"]) == 7

    with allure.step("Verify every FAQ answer contains its key guidance"):
        for answer, keyword in zip(
            faqs["answers"], warranty.FAQ_ANSWER_KEYWORDS
        ):
            assert keyword.lower() in answer.lower()

    with allure.step("Verify every FAQ question has correct published text"):
        assert faqs["questions"] == warranty.FAQ_QUESTIONS
