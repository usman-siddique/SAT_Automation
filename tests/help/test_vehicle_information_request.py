import allure

from pages.help.help_page import HelpPage
from pages.help.vehicle_information_request_page import (
    VehicleInformationRequestPage,
)


def test_vehicle_information_request_page(page_no_login):
    HelpPage(page_no_login).open_menu_item(
        "Vehicle Information Request",
        "/request-vehicle-information",
        "h1:has-text('Request Vehicle Information')",
    )
    request_page = VehicleInformationRequestPage(page_no_login)

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


def test_vehicle_information_request_empty_required_fields(page_no_login):
    HelpPage(page_no_login).open_menu_item(
        "Vehicle Information Request",
        "/request-vehicle-information",
        "h1:has-text('Request Vehicle Information')",
    )
    request_page = VehicleInformationRequestPage(page_no_login)

    with allure.step("Check the empty required vehicle-request fields"):
        messages = request_page.get_empty_form_validation_messages()
        assert set(messages) == {"make", "model", "email", "question"}
        assert all(messages.values())
