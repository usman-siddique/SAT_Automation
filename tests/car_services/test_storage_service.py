"""Business coverage for the SAT Vehicle Storage Service page."""

import allure

from pages.car_services.car_services_page import CarServicesPage
from pages.car_services.storage_service_page import StorageServicePage


def open_storage_service(page):
    CarServicesPage(page).go_to_storage_service()
    return StorageServicePage(page)


def test_storage_service_overview_and_policy(page_no_login):
    storage = open_storage_service(page_no_login)

    with allure.step("Verify page URL, heading, and all storage policy rules"):
        assert storage.verify_overview() == {
            "path": "/storage-policy",
            "heading": "Secure Storage Service For Your Vehicle's Safety",
            "policy_points": 7,
        }


def test_storage_service_country_fee_table(page_no_login):
    storage = open_storage_service(page_no_login)

    with allure.step("Verify all supported countries and fee periods"):
        fees = storage.get_storage_fees()
        assert [record["country"] for record in fees] == storage.COUNTRIES

    with allure.step("Verify Japan's first 30 days and later fees"):
        japan = fees[0]
        assert japan["days_1_30"] == "Free of cost"
        assert japan["days_31_60"] == "JPY 10,000/ $90"
        assert japan["days_61_90"] == "JPY 20,000/ $190"

    with allure.step("Verify all other country fee rows are consistent"):
        for record in fees[1:]:
            assert record["days_1_30_icon"], (
                f"{record['country']} is missing its 1-30 day check icon."
            )
            expected_31_60 = (
                "JPY 20,000/ $90"
                if record["country"] == "Uganda"
                else "JPY 10,000/ $90"
            )
            assert record["days_31_60"] == expected_31_60, (
                f"Unexpected 31-60 day fee for {record['country']}: "
                f"{record['days_31_60']}"
            )
            assert record["days_61_90"] == "JPY 20,000/ $190"


def test_storage_service_benefits_and_use_cases(page_no_login):
    storage = open_storage_service(page_no_login)

    with allure.step("Verify all four Storage Service benefits and icons"):
        assert storage.verify_benefits() == storage.BENEFITS

    with allure.step("Verify all three vehicle-storage use cases and images"):
        assert storage.verify_use_cases() == storage.USE_CASES
