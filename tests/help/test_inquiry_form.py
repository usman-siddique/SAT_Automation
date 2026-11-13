import allure
import pytest

from config import INQUIRY_FORM_DATA
from pages.help.help_page import HelpPage
from pages.help.inquiry_form_page import InquiryFormPage


def open_inquiry_form(page):
    HelpPage(page).open_menu_item(
        "Inquiry Form",
        "/inquiry-form",
        "h1:has-text('Inquiry Form:')",
    )
    return InquiryFormPage(page)


def test_inquiry_form_page(page_no_login):
    inquiry = open_inquiry_form(page_no_login)

    with allure.step("Verify the Inquiry Form heading"):
        assert inquiry.get_heading() == "Inquiry Form:"

    with allure.step("Verify all Inquiry Form fields"):
        assert inquiry.get_visible_field_names() == [
            "name",
            "email",
            "phone",
            "country",
            "city",
            "question",
        ]

    with allure.step("Verify the visually marked required fields"):
        assert inquiry.get_required_field_names() == [
            "name",
            "email",
            "question",
        ]

    with allure.step("Verify the Inquiry Form submit action"):
        assert inquiry.get_submit_button_text() == "Send Inquiry"


@pytest.mark.flaky(reruns=0)
def test_inquiry_form_successful_submission(page_no_login):
    if not INQUIRY_FORM_DATA["email"]:
        pytest.skip(
            "Inquiry email is missing. Set INQUIRY_EMAIL or LOGIN_EMAIL in "
            "the private .env file."
        )

    inquiry = open_inquiry_form(page_no_login)

    with allure.step("Fill every Inquiry Form field"):
        inquiry.fill_form(INQUIRY_FORM_DATA)

    with allure.step("Submit the Inquiry Form and verify the success response"):
        result = inquiry.submit_and_get_success()
        assert result["status"] is True
        assert result["message"].strip()


def test_inquiry_form_validation_and_dynamic_cities(page_no_login):
    if not INQUIRY_FORM_DATA["email"]:
        pytest.skip(
            "Inquiry email is missing. Set INQUIRY_EMAIL or LOGIN_EMAIL in "
            "the private .env file."
        )

    inquiry = open_inquiry_form(page_no_login)

    with allure.step("Verify changing the country dynamically reloads cities"):
        assert inquiry.select_country_and_get_cities("Australia")

    with allure.step("Prepare a valid form as the validation baseline"):
        inquiry.fill_form(INQUIRY_FORM_DATA)

    validation_cases = [
        ("name", "   ", "This field is required"),
        ("email", "", "This field is required"),
        ("email", "invalid-email", "Enter valid Email."),
        ("question", "   ", "This field is required"),
        ("phone", "1", "Your phone number is incorrect"),
    ]
    valid_values = {
        "name": INQUIRY_FORM_DATA["name"],
        "email": INQUIRY_FORM_DATA["email"],
        "question": INQUIRY_FORM_DATA["question"],
        "phone": INQUIRY_FORM_DATA["phone"],
    }

    for field_name, invalid_value, expected_message in validation_cases:
        with allure.step(f"Verify invalid {field_name} does not submit"):
            inquiry.set_field_value(field_name, invalid_value)
            assert inquiry.submit_and_get_validation([field_name]) == {
                "errors": {field_name: expected_message},
                "post_count": 0,
            }
            inquiry.set_field_value(field_name, valid_values[field_name])

    with allure.step("Verify the 50-character name limit blocks submission"):
        inquiry.set_field_value("name", "N" * 51)
        assert inquiry.submit_and_get_validation(["name"]) == {
            "errors": {
                "name": "Name should not be greater than 50 characters."
            },
            "post_count": 0,
        }
