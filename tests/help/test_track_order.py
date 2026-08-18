import allure

from config import LOGIN_EMAIL, TRACK_ORDER_ID
from pages.help.help_page import HelpPage
from pages.help.track_order_page import TrackOrderPage


MISMATCHED_ORDER_EMAIL = "dealerflow2@gmail.com"


def test_track_order_without_login(page_no_login):
    HelpPage(page_no_login).open_menu_item(
        "Track Your Order",
        "/track-your-order",
        "h1:has-text('Track Your Order')",
    )
    tracking = TrackOrderPage(page_no_login)

    with allure.step("Verify the anonymous Track Your Order page"):
        assert tracking.get_heading() == "Track Your Order"

    with allure.step("Find the existing order using email and Order ID"):
        tracking.submit_order_lookup(TRACK_ORDER_ID, LOGIN_EMAIL)

    with allure.step("Verify the matching order summary"):
        assert page_no_login.url.endswith(
            f"/tracking-order-summary/{TRACK_ORDER_ID}"
        )
        assert tracking.get_order_summary_heading() == "Order Summary"
        assert tracking.has_order_id_label()


def test_track_order_rejects_mismatched_email(page_no_login):
    HelpPage(page_no_login).open_menu_item(
        "Track Your Order",
        "/track-your-order",
        "h1:has-text('Track Your Order')",
    )
    tracking = TrackOrderPage(page_no_login)

    with allure.step("Search an existing Order ID with a different email"):
        message = tracking.submit_mismatched_email(
            TRACK_ORDER_ID, MISMATCHED_ORDER_EMAIL
        )

    with allure.step("Verify the no-order validation message"):
        assert message == TrackOrderPage.NO_ORDER_MESSAGE
        assert page_no_login.url.endswith("/track-your-order")
