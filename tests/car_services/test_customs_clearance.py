import pytest

from pages.car_services.car_services_page import CarServicesPage
from pages.car_services.customs_clearance_page import CustomsClearancePage


@pytest.fixture
def customs_clearance(page_no_login):
    CarServicesPage(page_no_login).go_to_customs_clearance()
    return CustomsClearancePage(page_no_login)


class TestCustomsClearance:
    def test_main_heading(self, customs_clearance):
        customs_clearance.verify_main_heading()

    def test_image(self, customs_clearance):
        customs_clearance.verify_image()

    def test_steps_heading(self, customs_clearance):
        customs_clearance.verify_steps_heading()
