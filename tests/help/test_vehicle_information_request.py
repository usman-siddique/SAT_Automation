import allure
import pytest

from config import VEHICLE_INFORMATION_REQUEST_DATA
from pages.help.help_page import HelpPage
from pages.help.vehicle_information_request_page import (
    VehicleInformationRequestPage,
)


def open_vehicle_information_request(page):
    HelpPage(page).open_menu_item(
        "Vehicle Information Request",
        "/request-vehicle-information",
        "h1:has-text('Request Vehicle Information')",
    )
    return VehicleInformationRequestPage(page)


def test_vehicle_information_request_page(page_no_login):
    request_page = open_vehicle_information_request(page_no_login)

    with allure.step("Verify the Vehicle Information Request heading"):
        assert request_page.get_heading() == "Request Vehicle Information"

    with allure.step("Verify all vehicle-request fields"):
        assert request_page.get_visible_field_names() == [
            "make",
            "model",
            "body_type",
            "steering",
            "country",
            "email",
            "min_year",
            "max_year",
            "min_price",
            "max_price",
            "min_mileage",
            "max_mileage",
            "question",
        ]

    with allure.step("Verify the required vehicle-request fields"):
        assert request_page.get_required_field_names() == [
            "make",
            "model",
            "email",
            "question",
        ]

    with allure.step("Verify the Vehicle Information Request submit action"):
        assert request_page.get_submit_button_text() == "Send Inquiry"

    with allure.step("Verify Explore Used Cars by Make destinations"):
        assert request_page.get_popular_make_links() == [
            {"label": "Toyota", "path": "/used-cars/mk_toyota"},
            {"label": "Suzuki", "path": "/used-cars/mk_suzuki"},
            {"label": "Subaru", "path": "/used-cars/mk_subaru"},
            {"label": "Mazda", "path": "/used-cars/mk_mazda"},
            {"label": "Honda", "path": "/used-cars/mk_honda"},
            {"label": "Nissan", "path": "/used-cars/mk_nissan"},
        ]


def test_vehicle_information_request_validation_and_dependencies(page_no_login):
    request_page = open_vehicle_information_request(page_no_login)

    with allure.step("Verify empty required fields block submission"):
        result = request_page.submit_invalid_without_server_write(
            ["make", "model", "email", "question"]
        )
        assert result["post_count"] == 0
        assert all(
            not state["valid"]
            and state["value_missing"]
            and state["message"]
            for state in result["validation"].values()
        )

    with allure.step("Verify Make dynamically loads matching Models"):
        models = request_page.select_make_and_get_models("Toyota")
        assert "AQUA" in models

    with allure.step("Verify every optional filter accepts valid data"):
        request_page.fill_form(VEHICLE_INFORMATION_REQUEST_DATA)
        selected = request_page.get_selected_labels()
        for field_name, selected_label in selected.items():
            assert selected_label == VEHICLE_INFORMATION_REQUEST_DATA[field_name]

    with allure.step("Verify invalid email blocks submission"):
        request_page.set_email("invalid-email")
        result = request_page.submit_invalid_without_server_write(["email"])
        email = result["validation"]["email"]
        assert result["post_count"] == 0
        assert not email["valid"]
        assert email["type_mismatch"]
        assert email["message"]


@pytest.mark.flaky(reruns=0)
def test_vehicle_information_request_successful_submission(page_no_login):
    if not VEHICLE_INFORMATION_REQUEST_DATA["email"]:
        pytest.skip(
            "Vehicle-request email is missing. Set INQUIRY_EMAIL or "
            "LOGIN_EMAIL in the private .env file."
        )

    request_page = open_vehicle_information_request(page_no_login)

    with allure.step("Complete all Vehicle Information Request fields"):
        request_page.fill_form(VEHICLE_INFORMATION_REQUEST_DATA)

    with allure.step("Submit and verify the success response"):
        result = request_page.submit_and_get_success()
        assert result["status"] in (200, 302)
        assert "success" in result["message"].lower()
