import pytest

from pages.car_services.car_carrier_page import CarCarrierPage
from pages.car_services.car_services_page import CarServicesPage


@pytest.fixture
def car_carrier(page_no_login):
    CarServicesPage(page_no_login).go_to_car_carrier_service()
    return CarCarrierPage(page_no_login)


class TestCarCarrierService:
    def test_delivery_options_heading(self, car_carrier):
        car_carrier.verify_delivery_options_heading()

    def test_benefits_heading(self, car_carrier):
        car_carrier.verify_benefits_heading()

    def test_images(self, car_carrier):
        car_carrier.verify_images()
