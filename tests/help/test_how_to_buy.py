from urllib.parse import urlparse

import allure
import pytest

from config import (
    DEALER_LOGIN_EMAIL,
    DEALER_LOGIN_PASSWORD,
    ELIGIBLE_DEALER_USER_EMAIL,
    ELIGIBLE_DEALER_USER_PASSWORD,
)
from pages.help.help_page import HelpPage
from pages.help.how_to_buy_page import HowToBuyPage


def _open_how_to_buy(page):
    HelpPage(page).open_menu_item(
        "How to Buy",
        "/how-to-buy",
        "h1:has-text('How to Buy a Car with SAT')",
    )
    return HowToBuyPage(page)


def test_how_to_buy_page_content(page_no_login):
    how_to_buy = _open_how_to_buy(page_no_login)

    with allure.step("Verify the How to Buy heading"):
        assert how_to_buy.get_main_heading() == "How to Buy a Car with SAT"

    with allure.step("Verify the four vehicle-purchase steps"):
        assert how_to_buy.get_purchase_steps() == [
            "1. Search Vehicle",
            "2. Buy Now or Reserve",
            "3. Track Your Order",
            "4. Receive Delivery",
        ]


def test_how_to_buy_video_plays(page_no_login):
    how_to_buy = _open_how_to_buy(page_no_login)

    with allure.step("Verify the expected YouTube video is embedded"):
        assert (
            "youtube-nocookie.com/embed/T_RWR68iLDg"
            in how_to_buy.get_video_source()
        )

    with allure.step("Start the video and verify playback advances"):
        state = how_to_buy.play_video()
        assert state["error_code"] is None
        assert not state["paused"]
        assert state["current_time"] > 0
        assert state["ready_state"] >= 2


def test_buy_used_cars_quick_action(page_no_login):
    how_to_buy = _open_how_to_buy(page_no_login)

    with allure.step("Open Used Cars from the How To Buy Quick Actions"):
        how_to_buy.open_quick_action(
            "Buy Used Cars", "/used-cars", expected_final_path="/used-cars"
        )

    with allure.step("Verify the Used Cars destination"):
        assert urlparse(page_no_login.url).path == "/used-cars"


def test_buy_new_cars_quick_action(page_no_login):
    how_to_buy = _open_how_to_buy(page_no_login)

    with allure.step("Open New Cars from the How To Buy Quick Actions"):
        how_to_buy.open_quick_action(
            "Buy New Cars", "/new-cars", expected_final_path="/new-cars"
        )

    with allure.step("Verify the New Cars destination"):
        assert urlparse(page_no_login.url).path == "/new-cars"


def test_become_dealer_quick_action_for_guest(page_no_login):
    how_to_buy = _open_how_to_buy(page_no_login)

    with allure.step("Open Become a Dealer without logging in"):
        how_to_buy.open_quick_action(
            "Become a Dealer",
            "/dealers/sign-up",
            expected_final_path="/dealers/sign-up",
            ready_locator="h2:has-text('Create an Account')",
        )

    with allure.step("Verify the guest Dealer-account screen"):
        assert how_to_buy.get_dealer_state_heading() == "Create an Account"


def test_become_dealer_quick_action_for_rejected_user(
    rejected_dealer_user_page,
):
    how_to_buy = _open_how_to_buy(rejected_dealer_user_page)

    with allure.step("Open Become a Dealer as the rejected User"):
        how_to_buy.open_quick_action(
            "Become a Dealer",
            "/dealers/join-as-dealer",
            expected_final_path="/dealers/join-as-dealer",
            ready_locator="h2:has-text('Your Dealer Account Was Rejected')",
        )

    with allure.step("Verify the rejected Dealer-account screen"):
        assert (
            how_to_buy.get_dealer_state_heading()
            == "Your Dealer Account Was Rejected"
        )


@pytest.mark.skipif(
    not ELIGIBLE_DEALER_USER_EMAIL or not ELIGIBLE_DEALER_USER_PASSWORD,
    reason="Eligible Dealer User credentials are missing from .env.",
)
def test_become_dealer_quick_action_for_eligible_user(
    eligible_dealer_user_page,
):
    how_to_buy = _open_how_to_buy(eligible_dealer_user_page)

    with allure.step("Open Become a Dealer as an eligible User"):
        how_to_buy.open_quick_action(
            "Become a Dealer",
            "/dealers/join-as-dealer",
            expected_final_path="/dealers/join-as-dealer",
            ready_locator="h2:has-text('Become a Dealer Today')",
        )

    with allure.step("Verify the Dealer application screen"):
        assert how_to_buy.get_dealer_state_heading() == "Become a Dealer Today"


@pytest.mark.skipif(
    not DEALER_LOGIN_EMAIL or not DEALER_LOGIN_PASSWORD,
    reason="Dealer credentials are missing from .env.",
)
def test_become_dealer_quick_action_for_existing_dealer(dealer_page):
    how_to_buy = _open_how_to_buy(dealer_page)

    with allure.step("Open Become a Dealer as an existing Dealer"):
        how_to_buy.open_quick_action(
            "Become a Dealer",
            "/dealers/join-as-dealer",
            expected_final_path="/dealers/join-as-dealer",
            ready_locator="h2:has-text('You Already Have a Dealer Account')",
        )

    with allure.step("Verify the existing Dealer-account screen"):
        assert (
            how_to_buy.get_dealer_state_heading()
            == "You Already Have a Dealer Account"
        )


def test_how_to_buy_frequently_asked_questions(page_no_login):
    how_to_buy = _open_how_to_buy(page_no_login)

    with allure.step("Verify all five FAQ questions"):
        assert how_to_buy.get_faq_questions() == [
            question for question, _ in HowToBuyPage.FAQ_CONTENT
        ]

    with allure.step("Expand and verify every FAQ answer"):
        assert how_to_buy.get_faq_content() == list(HowToBuyPage.FAQ_CONTENT)
