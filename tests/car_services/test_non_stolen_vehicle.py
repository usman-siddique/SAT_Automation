"""Business coverage for the SAT Non-Stolen Vehicle Check service."""

from urllib.parse import urlparse

import allure
import pytest

from config import NON_STOLEN_VEHICLE_DATA
from pages.car_services.car_services_page import CarServicesPage
from pages.car_services.non_stolen_vehicle_page import NonStolenVehiclePage


def open_non_stolen_vehicle(page):
    CarServicesPage(page).go_to_non_stolen_vehicle()
    return NonStolenVehiclePage(page)


def test_non_stolen_vehicle_overview_and_certificate_process(page_no_login):
    non_stolen = open_non_stolen_vehicle(page_no_login)

    with allure.step(
        "Verify page overview, loaded banner, certificate rules, and four steps"
    ):
        overview = non_stolen.verify_overview_and_process()
        assert overview["path"] == "/non-stolen-vehicle"
        assert overview["steps"] == non_stolen.PROCESS_STEPS


def test_non_stolen_vehicle_valid_stock_and_payment_form(page_no_login):
    non_stolen = open_non_stolen_vehicle(page_no_login)

    with allure.step("Open and verify the Non-Stolen Vehicle form contract"):
        non_stolen.open_modal()
        non_stolen.verify_form_contract()

    with allure.step(
        "Load the configured stock and verify all vehicle details and service fee"
    ):
        details = non_stolen.lookup_stock(
            NON_STOLEN_VEHICLE_DATA["valid_stock_id"]
        )
        assert set(details) == {
            "name",
            "year",
            "engine",
            "mileage",
            "transmission",
        }


def test_non_stolen_vehicle_successful_test_card_submission(page_no_login):
    non_stolen = open_non_stolen_vehicle(page_no_login)
    if urlparse(page_no_login.url).hostname != "development.satjapan.info":
        pytest.skip("Payment submission is restricted to Development.")

    with allure.step("Load the configured vehicle and fill valid customer data"):
        non_stolen.open_modal()
        non_stolen.lookup_stock(
            NON_STOLEN_VEHICLE_DATA["valid_stock_id"]
        )
        entered = non_stolen.fill_valid_submission(
            NON_STOLEN_VEHICLE_DATA
        )
        assert entered["email"] == NON_STOLEN_VEHICLE_DATA["email"]
        expected_last_four = NON_STOLEN_VEHICLE_DATA["payment_card"][
            "number"
        ].replace(" ", "")[-4:]
        assert entered["card_last_four"] == expected_last_four

    with allure.step(
        "Submit the test-card payment and verify both successful API responses"
    ):
        result = non_stolen.submit_and_verify_payment()
        assert result["intent_status"] is True
        assert result["submission_status"] is True
        assert urlparse(result["page_url"]).path == "/non-stolen-vehicle"


def test_non_stolen_vehicle_negative_validation_blocks_payment(page_no_login):
    non_stolen = open_non_stolen_vehicle(page_no_login)
    non_stolen.open_modal()

    with allure.step(
        "Verify invalid stock, missing fields, and invalid email without payment"
    ):
        result = non_stolen.verify_negative_validation(
            NON_STOLEN_VEHICLE_DATA["valid_stock_id"],
            NON_STOLEN_VEHICLE_DATA["invalid_stock_id"],
        )
        assert result["payment_requests"] == []
