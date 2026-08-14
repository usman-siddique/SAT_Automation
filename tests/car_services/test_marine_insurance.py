import allure
import pytest

from pages.car_services.car_services_page import CarServicesPage
from pages.car_services.marine_insurance_page import MarineInsurancePage


@pytest.fixture
def marine_insurance(page_no_login):
    CarServicesPage(page_no_login).go_to_marine_insurance()
    return MarineInsurancePage(page_no_login)


def test_marine_insurance_page_content(marine_insurance):
    with allure.step("Verify Marine Insurance banner"):
        marine_insurance.verify_banner_image()

    with allure.step("Verify Marine Insurance coverage heading"):
        marine_insurance.verify_coverage_heading()

    with allure.step("Verify Marine Insurance steps heading"):
        marine_insurance.verify_steps_heading()
