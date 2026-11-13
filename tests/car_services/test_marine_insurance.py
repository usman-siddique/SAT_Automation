"""Business coverage for the SAT Marine Insurance service."""

import allure

from pages.car_services.car_services_page import CarServicesPage
from pages.car_services.marine_insurance_page import MarineInsurancePage


def open_marine_insurance(page):
    CarServicesPage(page).go_to_marine_insurance()
    return MarineInsurancePage(page)


def test_marine_insurance_overview_and_insurance_promise(page_no_login):
    marine = open_marine_insurance(page_no_login)

    with allure.step(
        "Verify page overview, loaded banner, and shipment-damage promise"
    ):
        overview = marine.verify_overview()
        assert overview == {
            "path": "/marine-insurance-services",
            "heading": (
                "Get full coverage up to the cost of the vehicle with our "
                "Marine Insurance Service"
            ),
            "detail_heading": "Detail",
        }


def test_marine_insurance_coverage_and_benefits(page_no_login):
    marine = open_marine_insurance(page_no_login)

    with allure.step(
        "Verify all four coverage areas, benefits, and coverage icons"
    ):
        assert marine.verify_coverage_and_benefits() == {
            "coverage": marine.COVERAGE_ITEMS,
            "benefits": marine.BENEFITS,
        }


def test_marine_insurance_service_process(page_no_login):
    marine = open_marine_insurance(page_no_login)

    with allure.step(
        "Verify all four Marine Insurance steps, guidance, and icons"
    ):
        assert marine.verify_process_steps() == marine.PROCESS_STEPS
