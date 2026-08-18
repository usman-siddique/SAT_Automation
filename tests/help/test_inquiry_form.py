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

    with allure.step("Verify the required Inquiry Form fields"):
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


@pytest.mark.parametrize("missing_field", ["name", "email", "question"])
def test_inquiry_form_missing_required_field(page_no_login, missing_field):
    if not INQUIRY_FORM_DATA["email"] and missing_field != "email":
        pytest.skip(
            "Inquiry email is missing. Set INQUIRY_EMAIL or LOGIN_EMAIL in "
            "the private .env file."
        )

    inquiry = open_inquiry_form(page_no_login)

    with allure.step(f"Fill the form without the required {missing_field} field"):
        inquiry.fill_form(INQUIRY_FORM_DATA, omitted_field=missing_field)

    with allure.step("Verify required-field validation and no submission"):
        assert inquiry.submit_and_get_validation(missing_field) == (
            "This field is required"
        )


def test_inquiry_form_invalid_email(page_no_login):
    inquiry = open_inquiry_form(page_no_login)
    invalid_data = {**INQUIRY_FORM_DATA, "email": "invalid-email"}

    with allure.step("Fill the Inquiry Form with an invalid email"):
        inquiry.fill_form(invalid_data)

    with allure.step("Verify email validation and no submission"):
        assert inquiry.submit_and_get_invalid_email_validation() == (
            "Enter valid Email."
        )
