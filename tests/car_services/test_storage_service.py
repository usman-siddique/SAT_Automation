import allure
import pytest

from pages.car_services.car_services_page import CarServicesPage
from pages.car_services.storage_service_page import StorageServicePage


@pytest.fixture
def storage(page_no_login):
    CarServicesPage(page_no_login).go_to_storage_service()
    return StorageServicePage(page_no_login)


def test_storage_service_page_content(storage):
    with allure.step("Verify Storage Service main heading"):
        assert (
            storage.get_main_heading()
            == "Secure Storage Service For Your Vehicle's Safety"
        )

    with allure.step("Verify supported-countries heading"):
        assert (
            storage.get_countries_heading()
            == "Countries Where We Offer Storage Service"
        )

    with allure.step("Verify Storage Service benefits heading"):
        assert (
            storage.get_benefits_heading()
            == "Benefits of SAT Vehicle Storage Service"
        )

    with allure.step("Verify Why Store section heading"):
        assert storage.get_why_store_heading() == "Why Store a New Vehicle?"
