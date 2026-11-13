"""Business coverage for the SAT Car Carrier Service page."""

import allure

from pages.car_services.car_carrier_page import CarCarrierPage
from pages.car_services.car_services_page import CarServicesPage


def open_car_carrier(page):
    CarServicesPage(page).go_to_car_carrier_service()
    return CarCarrierPage(page)


def test_car_carrier_overview_and_delivery_options(page_no_login):
    carrier = open_car_carrier(page_no_login)

    with allure.step("Verify page overview, hero banner, and service details"):
        overview = carrier.verify_overview()
        assert overview["path"] == "/car-carrier"
        assert overview["heading"].endswith("Car Carrier Service")

    with allure.step("Verify both delivery options, descriptions, and images"):
        assert carrier.verify_delivery_options() == carrier.DELIVERY_OPTIONS


def test_car_carrier_service_benefits(page_no_login):
    carrier = open_car_carrier(page_no_login)

    with allure.step("Verify all four Car Carrier Service benefits"):
        assert carrier.verify_benefits() == carrier.BENEFITS


def test_car_carrier_process_steps(page_no_login):
    carrier = open_car_carrier(page_no_login)

    with allure.step("Verify all three process steps, guidance, and icons"):
        assert carrier.verify_process_steps() == carrier.PROCESS_STEPS
