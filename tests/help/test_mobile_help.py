from urllib.parse import urlparse

import allure

from config import BASE_URL
from pages.help.dealer_page import DealerPage
from pages.help.faq_page import FaqPage
from pages.help.inquiry_form_page import InquiryFormPage
from pages.help.mobile_help_page import MobileHelpPage
from pages.help.seller_registration_page import SellerRegistrationPage
from pages.help.track_order_page import TrackOrderPage
from pages.help.vehicle_information_request_page import (
    VehicleInformationRequestPage,
)


def _open_mobile_home(page):
    response = page.goto(
        BASE_URL,
        wait_until="domcontentloaded",
        timeout=60000,
    )
    assert response is None or response.status < 500
    page.locator("#navbar_mobile_header").wait_for(
        state="visible",
        timeout=10000,
    )


def _open_mobile_destination(page, name):
    destination = next(
        item for item in MobileHelpPage.DESTINATIONS if item[0] == name
    )
    MobileHelpPage(page).open_item(*destination)
    return destination


def test_mobile_help_menu_and_all_destinations(mobile_page):
    mobile_help = MobileHelpPage(mobile_page)
    expected_names = [item[0] for item in MobileHelpPage.DESTINATIONS]
    expected_paths = [item[1] for item in MobileHelpPage.DESTINATIONS]

    with allure.step("Open the touch Help menu and verify every item"):
        assert mobile_help.get_item_names() == expected_names
        assert mobile_help.get_item_paths() == expected_paths
        mobile_help.assert_elements_usable(
            mobile_page.locator("#offcanvascarhelp a:visible"),
            "mobile Help links",
        )

    for index, (name, path, ready_locator) in enumerate(
        MobileHelpPage.DESTINATIONS
    ):
        if index:
            _open_mobile_home(mobile_page)
        with allure.step(f"Open and verify the mobile Help destination: {name}"):
            mobile_help.open_item(name, path, ready_locator)
            assert urlparse(mobile_page.url).path.rstrip("/") == path
            mobile_help.assert_page_layout(
                name,
                ready_locator,
                require_mobile_header=(
                    name != "Become a SAT Japan Dealer"
                ),
            )


def test_mobile_inquiry_form_layout_validation_and_duplicate_clicks(
    mobile_page,
):
    _open_mobile_destination(mobile_page, "Inquiry Form")
    inquiry = InquiryFormPage(mobile_page)
    mobile_help = MobileHelpPage(mobile_page)

    with allure.step("Verify the complete Inquiry form is usable on mobile"):
        assert inquiry.get_visible_field_names() == [
            "name",
            "email",
            "phone",
            "country",
            "city",
            "question",
        ]
        assert inquiry.get_submit_button_text() == "Send Inquiry"
        mobile_help.assert_page_layout(
            "Inquiry Form",
            "h1:has-text('Inquiry Form:')",
        )
        mobile_help.assert_elements_usable(
            mobile_page.locator(
                "#formInquiry input:visible, #formInquiry select:visible, "
                "#formInquiry textarea:visible, #formInquiry button:visible"
            ),
            "Inquiry form controls",
        )

    with allure.step("Double-click a boundary-invalid Inquiry safely"):
        inquiry.set_field_value("name", "N" * 51)
        inquiry.set_field_value("email", "mobile.qa@example.com")
        inquiry.set_field_value("question", "Mobile boundary validation")
        assert inquiry.submit_and_get_validation(
            ["name"],
            click_count=2,
        ) == {
            "errors": {
                "name": "Name should not be greater than 50 characters."
            },
            "post_count": 0,
        }


def test_mobile_vehicle_request_layout_validation_and_duplicate_clicks(
    mobile_page,
):
    _open_mobile_destination(mobile_page, "Vehicle Information Request")
    request_page = VehicleInformationRequestPage(mobile_page)
    mobile_help = MobileHelpPage(mobile_page)

    with allure.step("Verify every vehicle-request field is usable on mobile"):
        assert request_page.get_required_field_names() == [
            "make",
            "model",
            "email",
            "question",
        ]
        mobile_help.assert_page_layout(
            "Vehicle Information Request",
            "h1:has-text('Request Vehicle Information')",
        )
        mobile_help.assert_elements_usable(
            mobile_page.locator(
                "form[action*='/store-request-a-car'] input[name]:visible, "
                "form[action*='/store-request-a-car'] textarea:visible, "
                "form[action*='/store-request-a-car'] "
                ".select2-selection:visible, "
                "form[action*='/store-request-a-car'] button:visible"
            ),
            "Vehicle Information Request controls",
        )

    with allure.step("Double-click an empty request without a server write"):
        result = request_page.submit_invalid_without_server_write(
            ["make", "model", "email", "question"],
            click_count=2,
        )
        assert result["post_count"] == 0
        assert all(
            not state["valid"]
            and state["value_missing"]
            and state["message"]
            for state in result["validation"].values()
        )


def test_mobile_faq_form_layout_validation_and_duplicate_clicks(mobile_page):
    _open_mobile_destination(mobile_page, "FAQs")
    faq = FaqPage(mobile_page)
    mobile_help = MobileHelpPage(mobile_page)

    with allure.step("Verify the FAQ question form is usable on mobile"):
        assert faq.get_question_form_details() == {
            "heading": "Still Have Any Question?",
            "question_required": True,
            "name_required": True,
            "email_required": True,
            "email_type": "email",
            "remember_visible": True,
            "submit_visible": True,
        }
        mobile_help.assert_page_layout("FAQs", "#faq_search_input")
        mobile_help.assert_elements_usable(
            mobile_page.locator(
                "form[action$='/faq-store'] input:visible, "
                "form[action$='/faq-store'] textarea:visible, "
                "form[action$='/faq-store'] button:visible"
            ),
            "FAQ question controls",
        )

    with allure.step("Double-click an empty FAQ submission safely"):
        result = faq.get_question_form_validation(
            "",
            "",
            "",
            click_count=2,
        )
        assert result["post_count"] == 0
        assert all(
            not result["fields"][field]["valid"]
            and result["fields"][field]["value_missing"]
            and result["fields"][field]["message"]
            for field in ("question", "name", "email")
        )


def test_mobile_track_order_layout_validation_and_duplicate_clicks(
    mobile_page,
):
    _open_mobile_destination(mobile_page, "Track Your Order")
    tracking = TrackOrderPage(mobile_page)
    mobile_help = MobileHelpPage(mobile_page)

    with allure.step("Verify Track Your Order is usable on mobile"):
        assert tracking.get_form_details() == {
            "order_visible": True,
            "order_required": True,
            "email_visible": True,
            "email_required": True,
            "email_type": "email",
            "submit_visible": True,
        }
        mobile_help.assert_page_layout(
            "Track Your Order",
            "h1:has-text('Track Your Order')",
        )
        mobile_help.assert_elements_usable(
            mobile_page.locator(
                "input[name='order_no']:visible, input[name='email']:visible, "
                "button:has-text('Submit'):visible"
            ),
            "Track Your Order controls",
        )

    with allure.step("Double-click empty tracking fields without a POST"):
        result = tracking.get_client_validation("", "", click_count=2)
        assert result["post_count"] == 0
        for field in ("order", "email"):
            assert result[field]["valid"] is False
            assert result[field]["value_missing"] is True
            assert result[field]["message"]


def test_mobile_dealer_form_layout_validation_and_duplicate_clicks(
    mobile_page,
):
    _open_mobile_destination(mobile_page, "Become a SAT Japan Dealer")
    dealer = DealerPage(mobile_page)
    mobile_help = MobileHelpPage(mobile_page)

    with allure.step("Verify the guest Dealer form is usable on mobile"):
        assert dealer.get_account_state_heading() == "Create an Account"
        assert dealer.get_create_account_form()["fields"] == [
            "dealer_email",
            "dealer_name",
            "dealer_phone",
            "company_name",
            "your_position",
        ]

    with allure.step("Double-click invalid Dealer details without creation"):
        dealer.fill_create_account_details(
            {
                "email": "invalid-email",
                "name": "Mobile Dealer QA",
                "phone": "3001252502",
                "company": "SAT Mobile QA",
                "position": "QA Engineer",
            }
        )
        assert dealer.click_create_next_without_server_write(
            click_count=2
        ) == []
        assert "@" in dealer.get_email_validation_message()
        assert dealer.get_account_state_heading() == "Create an Account"

    with allure.step("Verify Dealer controls fit and remain usable"):
        mobile_help.assert_page_layout(
            "Become a SAT Japan Dealer",
            "#dealer-create-form",
            require_mobile_header=False,
        )
        mobile_help.assert_elements_usable(
            mobile_page.locator(
                "#dealer-create-form input:visible, "
                "#dealer-create-form select:visible, "
                "#dealer-create-form button:visible"
            ),
            "Dealer account controls",
        )


def test_mobile_seller_form_layout_validation_and_duplicate_clicks(
    mobile_page,
):
    _open_mobile_destination(mobile_page, "Become a Seller with SAT")
    seller = SellerRegistrationPage(mobile_page)
    mobile_help = MobileHelpPage(mobile_page)

    with allure.step("Verify Seller Registration is usable on mobile"):
        assert seller.get_active_step() == 1
        assert seller.get_active_field_names() == [
            "company_name",
            "country",
            "registration_number",
            "website",
        ]
        mobile_help.assert_page_layout(
            "Seller Registration",
            "#sellerApplicationForm",
        )
        mobile_help.assert_elements_usable(
            mobile_page.locator(
                "#sellerApplicationForm .seller-step-section:not(.d-none) "
                "input[name]:visible, "
                "#sellerApplicationForm .seller-step-section:not(.d-none) "
                ".select2-selection:visible, "
                "#sellerApplicationForm .seller-step-section:not(.d-none) "
                "button:visible"
            ),
            "Seller Registration controls",
        )

    with allure.step("Double-click empty Seller fields without a record"):
        result = seller.continue_without_submission(click_count=2)
        assert result == {
            "step": 1,
            "errors": [
                "Please enter your company name.",
                "Please select your country.",
                "Please enter your company registration number.",
            ],
            "post_count": 0,
        }
