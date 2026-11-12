import os

import allure
import pytest

from config import (
    SELLER_REGISTRATION_DATA,
    SELLER_REGISTRATION_DOCUMENT,
)
from pages.help.help_page import HelpPage
from pages.help.seller_registration_page import SellerRegistrationPage


LANGUAGE_CASES = [
    {
        "language": "English",
        "path": "/seller-registration",
        "heading": "Company",
        "step_labels": [
            "Company",
            "Seller Information",
            "Verification",
        ],
        "step_one_errors": [
            "Please enter your company name.",
            "Please select your country.",
            "Please enter your company registration number.",
        ],
        "step_two_errors": [
            "Please enter the contact person's name.",
            "Please enter your business email.",
            "Please enter your phone number.",
            "Please select a seller type.",
            "Please select your monthly vehicle availability.",
            "Please enter your vehicle location.",
            "Please select at least one vehicle type.",
        ],
        "step_three_errors": [
            "Please upload your company registration document.",
            "Please confirm the agreement to continue.",
        ],
        "invalid_email": "Please enter a valid email address.",
        "invalid_phone": (
            "Please enter a valid phone number for the selected country."
        ),
        "invalid_document_type": (
            "Please upload a PDF, JPG or PNG file."
        ),
        "oversized_document": "File size must be under 10 MB.",
        "uploaded": "Uploaded successfully",
    },
    {
        "language": "한국어",
        "path": "/seller-registration/korea",
        "heading": "회사 정보",
        "step_labels": ["회사 정보", "담당자 및 차량 정보", "인증"],
        "step_one_errors": [
            "회사명을 입력해 주세요.",
            "국가를 선택해 주세요.",
            "사업자등록번호를 입력해 주세요.",
        ],
        "step_two_errors": [
            "담당자 이름을 입력해 주세요.",
            "이메일을 입력해 주세요.",
            "전화번호 번호를 입력해 주세요.",
            "판매업체 유형을 선택해 주세요.",
            "월간 판매 가능 차량 수를 선택해 주세요.",
            "차량 보유 지역을 입력해 주세요.",
            "판매 차량 종류를 하나 이상 선택해 주세요.",
        ],
        "step_three_errors": [
            "회사 등록 서류를 업로드해 주세요.",
            "계속하려면 확인란에 동의해 주세요.",
        ],
        "invalid_email": "올바른 이메일 주소를 입력해 주세요.",
        "invalid_phone": (
            "선택한 국가에 맞는 올바른 전화번호를 입력해 주세요."
        ),
        "invalid_document_type": (
            "PDF, JPG 또는 PNG 파일을 업로드해 주세요."
        ),
        "oversized_document": "파일 크기는 10MB 이하여야 합니다.",
        "uploaded": "업로드 완료",
    },
    {
        "language": "日本語",
        "path": "/seller-registration/japan",
        "heading": "会社情報",
        "step_labels": ["会社情報", "担当者・車両情報", "本人確認"],
        "step_one_errors": [
            "会社名を入力してください。",
            "国を選択してください。",
            "会社登録番号を入力してください。",
        ],
        "step_two_errors": [
            "担当者名を入力してください。",
            "メールアドレスを入力してください。",
            "電話番号を入力してください。",
            "販売者の種類を選択してください。",
            "月間販売可能台数を選択してください。",
            "車両の所在地を入力してください。",
            "販売する車両の種類を1つ以上選択してください。",
        ],
        "step_three_errors": [
            "会社登録書類をアップロードしてください。",
            "続行するにはチェックボックスに同意してください。",
        ],
        "invalid_email": "有効なメールアドレスを入力してください。",
        "invalid_phone": (
            "選択した国に合った有効な電話番号を入力してください。"
        ),
        "invalid_document_type": (
            "PDF、JPG、PNGのいずれかのファイルをアップロードしてください。"
        ),
        "oversized_document": (
            "ファイルサイズは10MB以下にしてください。"
        ),
        "uploaded": "アップロード完了",
    },
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


def test_seller_registration_languages(page_no_login):
    seller = open_seller_registration(page_no_login)

    for language_case in LANGUAGE_CASES:
        language = language_case["language"]
        with allure.step(f"Switch Seller registration to {language}"):
            seller.switch_language(language, language_case["path"])

        with allure.step(
            f"Verify the {language} Seller registration labels"
        ):
            assert seller.current_path() == language_case["path"]
            assert seller.get_selected_language() == language
            assert seller.get_active_heading() == language_case["heading"]
            assert seller.get_stepper_labels() == language_case["step_labels"]


@pytest.mark.parametrize(
    "language_case",
    LANGUAGE_CASES,
    ids=["english", "korean", "japanese"],
)
def test_seller_registration_validation_and_navigation(
    page_no_login,
    language_case,
):
    seller = open_seller_registration(page_no_login)
    language = language_case["language"]
    seller.switch_language(language, language_case["path"])

    with allure.step(
        f"Verify {language} Step 1 required-field validation"
    ):
        assert seller.continue_without_submission() == {
            "step": 1,
            "errors": language_case["step_one_errors"],
            "post_count": 0,
        }

    with allure.step("Complete Step 1 without the optional website"):
        seller.fill_company(
            SELLER_REGISTRATION_DATA,
            include_website=False,
        ).continue_to_next_step()
        assert seller.get_active_step() == 2
        assert seller.get_active_field_names() == [
            "contact_name",
            "email",
            "phone_code",
            "phone_number",
            "seller_type",
            "monthly_availability",
            "vehicle_location[]",
        ]

    with allure.step(
        f"Verify {language} Step 2 required-field validation"
    ):
        assert seller.continue_without_submission() == {
            "step": 2,
            "errors": language_case["step_two_errors"],
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
            "errors": [language_case["invalid_email"]],
            "post_count": 0,
        }

    with allure.step("Verify invalid phone-number validation"):
        page_no_login.locator("[name='email']").fill(
            SELLER_REGISTRATION_DATA["email"]
        )
        seller.set_phone_number("1")
        assert seller.continue_without_submission() == {
            "step": 2,
            "errors": [language_case["invalid_phone"]],
            "post_count": 0,
        }

    with allure.step("Fix the phone number and open Verification"):
        seller.set_phone_number(
            SELLER_REGISTRATION_DATA["phone_number"]
        )
        seller.continue_to_next_step()
        assert seller.get_active_step() == 3

    with allure.step(
        f"Verify {language} Step 3 required-field validation"
    ):
        assert seller.submit_invalid_without_server_write() == {
            "step": 3,
            "errors": language_case["step_three_errors"],
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
        assert seller.upload_invalid_type(
            language_case["invalid_document_type"]
        ) == language_case["invalid_document_type"]
        assert seller.upload_oversized_document(
            language_case["oversized_document"]
        ) == language_case["oversized_document"]

    with allure.step("Verify valid upload preview and removal"):
        seller.upload_document(SELLER_REGISTRATION_DOCUMENT)
        preview = seller.get_document_preview()
        assert preview["name"] == os.path.basename(
            SELLER_REGISTRATION_DOCUMENT
        )
        assert language_case["uploaded"] in preview["meta"]
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
