import allure
import pytest

from pages.car_services.car_carrier_page import CarCarrierPage
from pages.car_services.car_services_page import CarServicesPage


@pytest.fixture
def car_carrier(page_no_login):
    CarServicesPage(page_no_login).go_to_car_carrier_service()
    return CarCarrierPage(page_no_login)


def test_car_carrier_page_content(car_carrier):
    with allure.step("Verify Delivery Options heading"):
        car_carrier.verify_delivery_options_heading()

    with allure.step("Verify carrier-service benefits heading"):
        car_carrier.verify_benefits_heading()

    with allure.step("Verify both carrier images are visible and loaded"):
        car_carrier.verify_images()
