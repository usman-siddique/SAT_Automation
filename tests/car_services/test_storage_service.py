import pytest

from pages.car_services.car_services_page import CarServicesPage
from pages.car_services.storage_service_page import StorageServicePage


@pytest.fixture
def storage(page_no_login):
    CarServicesPage(page_no_login).go_to_storage_service()
    return StorageServicePage(page_no_login)


class TestStorageService:
    def test_main_heading(self, storage):
        assert (
            storage.get_main_heading()
            == "Secure Storage Service For Your Vehicle's Safety"
        )

    def test_countries_heading(self, storage):
        assert (
            storage.get_countries_heading()
            == "Countries Where We Offer Storage Service"
        )

    def test_benefits_heading(self, storage):
        assert (
            storage.get_benefits_heading()
            == "Benefits of SAT Vehicle Storage Service"
        )

    def test_why_store_heading(self, storage):
        assert storage.get_why_store_heading() == "Why Store a New Vehicle?"
