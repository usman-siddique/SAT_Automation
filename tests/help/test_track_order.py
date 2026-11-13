import allure

from config import (
    TRACK_ORDER_EMAIL,
    TRACK_ORDER_ID,
    TRACK_ORDER_MISMATCH_EMAIL,
    TRACK_ORDER_UNKNOWN_ID,
)
from pages.help.help_page import HelpPage
from pages.help.track_order_page import TrackOrderPage


def open_track_order(page):
    HelpPage(page).open_menu_item(
        "Track Your Order",
        "/track-your-order",
        "h1:has-text('Track Your Order')",
    )
    return TrackOrderPage(page)


def test_track_order_validation_and_negative_cases(page_no_login):
    tracking = open_track_order(page_no_login)

    with allure.step("Verify the Track Your Order form structure"):
        assert tracking.get_heading() == "Track Your Order"
        assert tracking.get_form_details() == {
            "order_visible": True,
            "order_required": True,
            "email_visible": True,
            "email_required": True,
            "email_type": "email",
            "submit_visible": True,
        }

    with allure.step("Verify both required fields block submission"):
        result = tracking.get_client_validation("", "")
        assert result["order"]["valid"] is False
        assert result["order"]["value_missing"] is True
        assert result["order"]["message"]
        assert result["email"]["valid"] is False
        assert result["email"]["value_missing"] is True
        assert result["email"]["message"]
        assert result["post_count"] == 0

    with allure.step("Verify an invalid email format blocks submission"):
        result = tracking.get_client_validation(TRACK_ORDER_ID, "invalid-email")
        assert result["order"]["valid"] is True
        assert result["email"]["valid"] is False
        assert result["email"]["type_mismatch"] is True
        assert result["email"]["message"]
        assert result["post_count"] == 0

    with allure.step("Verify the correct order with another user's email"):
        message = tracking.submit_invalid_lookup(
            TRACK_ORDER_ID, TRACK_ORDER_MISMATCH_EMAIL
        )
        assert message == TrackOrderPage.NO_ORDER_MESSAGE
        assert page_no_login.url.endswith("/track-your-order")

    with allure.step("Verify an unknown order with the correct email"):
        message = tracking.submit_invalid_lookup(
            TRACK_ORDER_UNKNOWN_ID, TRACK_ORDER_EMAIL
        )
        assert message == TrackOrderPage.NO_ORDER_MESSAGE
        assert page_no_login.url.endswith("/track-your-order")


def test_track_order_existing_order_summary(page_no_login):
    tracking = open_track_order(page_no_login)

    with allure.step("Find the existing order using email and Order ID"):
        tracking.submit_order_lookup(TRACK_ORDER_ID, TRACK_ORDER_EMAIL)

    with allure.step("Verify the matching order summary"):
        assert page_no_login.url.endswith(
            f"/tracking-order-summary/{TRACK_ORDER_ID}"
        )
        assert tracking.get_order_summary_heading() == "Order Summary"
        assert tracking.has_order_id_label()
        assert tracking.has_order_id_value(TRACK_ORDER_ID)
