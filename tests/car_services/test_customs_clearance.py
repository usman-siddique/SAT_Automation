import allure
import pytest

from pages.car_services.car_services_page import CarServicesPage
from pages.car_services.customs_clearance_page import CustomsClearancePage


@pytest.fixture
def customs_clearance(page_no_login):
    CarServicesPage(page_no_login).go_to_customs_clearance()
    return CustomsClearancePage(page_no_login)


def test_customs_clearance_page_content(customs_clearance):
    with allure.step("Verify Customs Clearance main heading"):
        customs_clearance.verify_main_heading()

    with allure.step("Verify Customs Clearance image"):
        customs_clearance.verify_image()

    with allure.step("Verify Customs Clearance steps heading"):
        customs_clearance.verify_steps_heading()
