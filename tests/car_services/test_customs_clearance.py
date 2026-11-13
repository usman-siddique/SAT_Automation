"""Business coverage for the SAT Customs Clearance Service page."""

import allure

from pages.car_services.car_services_page import CarServicesPage
from pages.car_services.customs_clearance_page import CustomsClearancePage


def open_customs_clearance(page):
    CarServicesPage(page).go_to_customs_clearance()
    return CustomsClearancePage(page)


def test_customs_clearance_overview_and_service_details(page_no_login):
    customs = open_customs_clearance(page_no_login)

    with allure.step("Verify page overview, service details, and images"):
        overview = customs.verify_overview()
        assert overview == {
            "path": "/customs-clearance",
            "heading": "Ensure Fast and Compliant Shipments",
            "service_heading": "Trouble-Free Customs Clearance",
        }


def test_customs_clearance_service_benefits(page_no_login):
    customs = open_customs_clearance(page_no_login)

    with allure.step("Verify all four Customs Clearance benefits"):
        assert customs.verify_benefits() == customs.BENEFITS


def test_customs_clearance_process_steps(page_no_login):
    customs = open_customs_clearance(page_no_login)

    with allure.step("Verify all four process steps, guidance, and icons"):
        assert customs.verify_process_steps() == customs.PROCESS_STEPS
