import os

import allure
import pytest

from config import (
    SELLER_REGISTRATION_DATA,
    SELLER_REGISTRATION_DOCUMENT,
)
from pages.help.help_page import HelpPage
from pages.help.seller_registration_page import SellerRegistrationPage


STEP_ONE_ERRORS = [
    "Please enter your company name.",
    "Please select your country.",
    "Please enter your company registration number.",
]
STEP_TWO_ERRORS = [
    "Please enter the contact person's name.",
    "Please enter your business email.",
    "Please enter your phone number.",
    "Please select a seller type.",
    "Please select your monthly vehicle availability.",
    "Please enter your vehicle location.",
    "Please select at least one vehicle type.",
]
STEP_THREE_ERRORS = [
    "Please upload your company registration document.",
    "Please confirm the agreement to continue.",
]

LANGUAGE_CASES = [
    pytest.param(
        "English",
        "/seller-registration",
        "Company",
        ["Company", "Seller Information", "Verification"],
        id="english",
    ),
    pytest.param(
        "한국어",
        "/seller-registration/korea",
        "회사 정보",
        ["회사 정보", "담당자 및 차량 정보", "인증"],
        id="korean",
    ),
    pytest.param(
        "日本語",
        "/seller-registration/japan",
        "会社情報",
        ["会社情報", "担当者・車両情報", "本人確認"],
        id="japanese",
    ),
]


def open_seller_registration(page):
    HelpPage(page).open_menu_item(
        "Become a Seller with SAT",
        "/seller-registration",
        "#sellerApplicationForm",
    )
    return SellerRegistrationPage(page)


def test_seller_registration_help_redirect_and_structure(page_no_login):
    seller = open_seller_registration(page_no_login)

    with allure.step("Verify the three-step Seller registration structure"):
        assert seller.get_stepper_labels() == [
            "Company",
            "Seller Information",
            "Verification",
        ]
        assert seller.get_active_step() == 1
        assert seller.get_active_heading() == "Company"
        assert seller.get_active_field_names() == [
            "company_name",
            "country",
            "registration_number",
            "website",
        ]


@pytest.mark.parametrize(
    ("language", "path", "heading", "step_labels"),
    LANGUAGE_CASES,
)
def test_seller_registration_languages(
    page_no_login,
    language,
    path,
    heading,
    step_labels,
):
    seller = open_seller_registration(page_no_login)

    with allure.step(f"Switch Seller registration to {language}"):
        seller.switch_language(language, path)

    with allure.step(f"Verify the {language} Seller registration labels"):
        assert seller.current_path() == path
        assert seller.get_selected_language() == language
        assert seller.get_active_heading() == heading
        assert seller.get_stepper_labels() == step_labels


def test_seller_registration_validation_and_navigation(page_no_login):
    seller = open_seller_registration(page_no_login)

    with allure.step("Verify Step 1 required fields block continuation"):
        assert seller.continue_without_submission() == {
            "step": 1,
            "errors": STEP_ONE_ERRORS,
            "post_count": 0,
        }

    with allure.step("Complete Step 1 without the optional website"):
        seller.fill_company(
            SELLER_REGISTRATION_DATA,
            include_website=False,
        ).continue_to_next_step()
        assert seller.get_active_heading() == "Contact & seller information"
        assert seller.get_active_field_names() == [
            "contact_name",
            "email",
            "phone_code",
            "phone_number",
            "seller_type",
            "monthly_availability",
            "vehicle_location[]",
        ]

    with allure.step("Verify Step 2 required fields block continuation"):
        assert seller.continue_without_submission() == {
            "step": 2,
            "errors": STEP_TWO_ERRORS,
            "post_count": 0,
        }

    with allure.step("Verify invalid business email validation"):
        seller.fill_seller_information(
            SELLER_REGISTRATION_DATA,
            email="invalid-email",
        )
        result = seller.continue_without_submission()
        assert result == {
            "step": 2,
            "errors": ["Please enter a valid email address."],
            "post_count": 0,
        }

    with allure.step("Verify invalid phone-number validation"):
        page_no_login.locator("[name='email']").fill(
            SELLER_REGISTRATION_DATA["email"]
        )
        seller.set_phone_number("1")
        assert seller.continue_without_submission() == {
            "step": 2,
            "errors": [
                "Please enter a valid phone number for the selected country."
            ],
            "post_count": 0,
        }

    with allure.step("Fix the phone number and open Verification"):
        seller.set_phone_number(
            SELLER_REGISTRATION_DATA["phone_number"]
        )
        seller.continue_to_next_step()
        assert seller.get_active_heading() == "Verification"

    with allure.step("Verify Step 3 requirements block submission"):
        assert seller.submit_invalid_without_server_write() == {
            "step": 3,
            "errors": STEP_THREE_ERRORS,
            "post_count": 0,
        }

    with allure.step("Verify Back preserves the completed Company data"):
        seller.go_back().go_back()
        assert seller.get_active_step() == 1
        assert seller.get_company_values() == {
            "company_name": SELLER_REGISTRATION_DATA["company_name"],
            "country": SELLER_REGISTRATION_DATA["country"],
            "registration_number": SELLER_REGISTRATION_DATA[
                "registration_number"
            ],
            "website": "",
        }
        seller.continue_to_next_step().continue_to_next_step()

    with allure.step("Verify document type and size validation"):
        assert seller.upload_invalid_type() == (
            "Please upload a PDF, JPG or PNG file."
        )
        assert seller.upload_oversized_document() == (
            "File size must be under 10 MB."
        )

    with allure.step("Verify valid upload preview and removal"):
        seller.upload_document(SELLER_REGISTRATION_DOCUMENT)
        preview = seller.get_document_preview()
        assert preview["name"] == os.path.basename(
            SELLER_REGISTRATION_DOCUMENT
        )
        assert "Uploaded successfully" in preview["meta"]
        assert seller.remove_document() == ""


@pytest.mark.flaky(reruns=0)
def test_seller_registration_successful_submission(page_no_login):
    seller = open_seller_registration(page_no_login)

    with allure.step("Complete Company details"):
        seller.fill_company(
            SELLER_REGISTRATION_DATA
        ).continue_to_next_step()

    with allure.step("Complete Contact and Seller Information"):
        seller.fill_seller_information(
            SELLER_REGISTRATION_DATA
        ).continue_to_next_step()

    with allure.step("Upload verification and submit the application"):
        seller.upload_document(SELLER_REGISTRATION_DOCUMENT)
        seller.confirm_agreement()
        result = seller.submit_and_get_result()
        allure.dynamic.parameter(
            "seller_email",
            SELLER_REGISTRATION_DATA["email"],
        )
        allure.dynamic.parameter("application_id", result["application_id"])

    with allure.step("Verify the submitted application is Under Review"):
        assert result["heading"] == "Application Submitted"
        assert result["application_id"].startswith("SEL-")
        assert result["status"] == "Under Review"
        assert result["return_visible"]
