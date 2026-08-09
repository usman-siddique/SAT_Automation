import pytest

from pages.car_services.car_services_page import CarServicesPage
from pages.car_services.marine_insurance_page import MarineInsurancePage


@pytest.fixture
def marine_insurance(page_no_login):
    CarServicesPage(page_no_login).go_to_marine_insurance()
    return MarineInsurancePage(page_no_login)


class TestMarineInsurance:
    def test_banner_image(self, marine_insurance):
        marine_insurance.verify_banner_image()

    def test_coverage_heading(self, marine_insurance):
        marine_insurance.verify_coverage_heading()

    def test_steps_heading(self, marine_insurance):
        marine_insurance.verify_steps_heading()
