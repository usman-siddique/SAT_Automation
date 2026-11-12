from datetime import datetime, timezone

import allure
import pytest

from config import (
    BASE_URL,
    DEALER_LOGIN_EMAIL,
    DEALER_LOGIN_PASSWORD,
    DEALER_TEST_PASSWORD,
    ELIGIBLE_DEALER_USER_EMAIL,
    ELIGIBLE_DEALER_USER_PASSWORD,
)
from pages.auth.login_page import LoginPage
from pages.help.dealer_page import DealerPage
from pages.help.help_page import HelpPage
from pages.help.how_to_buy_page import HowToBuyPage


CREATE_ACCOUNT_DATA = {
    "name": "Dealer SAT Automation",
    "phone": "3001252502",
    "company": "SAT QA Traders",
    "position": "QA Engineer",
}
JOIN_DEALER_DATA = {
    "name": "Dealer Join Automation",
    "phone": "3001252503",
    "dealership": "SAT Join QA Traders",
    "position": "QA Engineer",
    "website": "https://example.com",
}


def _unique_email(prefix):
    suffix = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S%f")
    return f"{prefix}{suffix}@gmail.com"


def _open_dealer_from_help(page, expected_path, ready_heading):
    HelpPage(page).open_menu_item(
        "Become a SAT Japan Dealer",
        expected_path,
        f"text={ready_heading}",
        expected_final_path=expected_path,
    )
    return DealerPage(page)


def _assert_create_account_form(dealer):
    assert dealer.get_account_state_heading() == "Create an Account"
    assert dealer.get_create_account_form() == {
        "fields": [
            "dealer_email",
            "dealer_name",
            "dealer_phone",
            "company_name",
            "your_position",
        ],
        "next_enabled": True,
    }


def _open_join_form_from_how_to_buy(page):
    HelpPage(page).open_menu_item(
        "How to Buy",
        "/how-to-buy",
        "h1:has-text('How to Buy a Car with SAT')",
    )
    HowToBuyPage(page).open_quick_action(
        "Become a Dealer",
        "/dealers/join-as-dealer",
        expected_final_path="/dealers/join-as-dealer",
        ready_locator="text=Become a Dealer Today",
    )
    return DealerPage(page)


def test_guest_help_dealer_link_opens_create_account(page_no_login):
    dealer = _open_dealer_from_help(
        page_no_login,
        "/dealers/sign-up",
        "Create an Account",
    )

    with allure.step("Verify the guest Dealer-account creation form"):
        _assert_create_account_form(dealer)


@pytest.mark.skipif(
    not ELIGIBLE_DEALER_USER_EMAIL or not ELIGIBLE_DEALER_USER_PASSWORD,
    reason="Eligible Dealer User credentials are missing from .env.",
)
def test_eligible_user_help_dealer_link_targets_join_form(
    eligible_dealer_user_page,
):
    with allure.step("Verify the eligible User Help link contract"):
        assert HelpPage(eligible_dealer_user_page).get_menu_item_path(
            "Become a SAT Japan Dealer"
        ) == "/dealers/join-as-dealer"


def test_become_dealer_for_rejected_user(rejected_dealer_user_page):
    dealer = _open_dealer_from_help(
        rejected_dealer_user_page,
        "/dealers/sign-up",
        "Your Dealer Account Was Rejected",
    )

    with allure.step("Verify the rejected Dealer-account screen"):
        assert (
            dealer.get_account_state_heading()
            == "Your Dealer Account Was Rejected"
        )


@pytest.mark.skipif(
    not DEALER_LOGIN_EMAIL or not DEALER_LOGIN_PASSWORD,
    reason="Dealer credentials are missing from .env.",
)
def test_become_dealer_link_hidden_for_existing_dealer(dealer_page):
    dealer = DealerPage(dealer_page)

    with allure.step("Verify Dealers cannot see the Become a Dealer link"):
        assert not dealer.is_main_dealer_link_visible()


def test_existing_dealer_how_to_buy_shows_existing_account(dealer_page):
    HelpPage(dealer_page).open_menu_item(
        "How to Buy",
        "/how-to-buy",
        "h1:has-text('How to Buy a Car with SAT')",
    )
    how_to_buy = HowToBuyPage(dealer_page)

    with allure.step("Open Become a Dealer from How to Buy"):
        how_to_buy.open_quick_action(
            "Become a Dealer",
            "/dealers/join-as-dealer",
            expected_final_path="/dealers/join-as-dealer",
            ready_locator="h2:has-text('You Already Have a Dealer Account')",
        )

    with allure.step("Verify the existing Dealer account state"):
        assert (
            DealerPage(dealer_page).get_account_state_heading()
            == "You Already Have a Dealer Account"
        )


def test_guest_signup_rejects_existing_dealer_email(page_no_login):
    dealer = _open_dealer_from_help(
        page_no_login,
        "/dealers/sign-up",
        "Create an Account",
    )

    with allure.step("Enter an existing Dealer email while logged out"):
        assert dealer.enter_existing_dealer_email(DEALER_LOGIN_EMAIL) == (
            "Dealer email already exists."
        )

    with allure.step("Verify the guest cannot continue with that email"):
        assert not dealer.get_create_account_form()["next_enabled"]


def test_guest_create_dealer_account_field_validation(page_no_login):
    dealer = _open_dealer_from_help(
        page_no_login,
        "/dealers/sign-up",
        "Create an Account",
    )
    email = _unique_email("dealer_account")
    data = {**CREATE_ACCOUNT_DATA, "email": "invalid-email"}

    with allure.step("Verify required first-step fields block continuation"):
        dealer.wait_for_create_account_next().click()
        assert dealer.get_account_state_heading() == "Create an Account"

    with allure.step("Verify invalid email format cannot open step two"):
        dealer.fill_create_account_details(data)
        dealer.wait_for_create_account_next().click()
        assert "@" in dealer.get_email_validation_message()
        assert dealer.get_account_state_heading() == "Create an Account"


@pytest.mark.flaky(reruns=0)
@pytest.mark.skipif(
    not DEALER_TEST_PASSWORD,
    reason="DEALER_TEST_PASSWORD is missing from .env.",
)
@pytest.mark.parametrize(
    ("password", "confirmation"),
    [
        pytest.param("12345", "12345", id="short-password"),
        pytest.param(
            DEALER_TEST_PASSWORD,
            "87654321",
            id="mismatched-confirmation",
        ),
    ],
)
def test_guest_create_dealer_account_password_validation(
    page_no_login,
    password,
    confirmation,
):
    dealer = _open_dealer_from_help(
        page_no_login,
        "/dealers/sign-up",
        "Create an Account",
    )
    email = _unique_email("dealer_validation_account")

    with allure.step("Open Additional Information with a unique email"):
        dealer.fill_create_account_details(
            {**CREATE_ACCOUNT_DATA, "email": email}
        )
        dealer.open_create_account_step_two()
        assert dealer.get_create_account_step_two() == {
            "fields": [
                "annual_revenue",
                "annual_imports",
                "password",
                "conform_password",
                "email_marketing",
            ],
            "create_button": "Create account",
        }

    with allure.step("Verify invalid passwords never reach account creation"):
        dealer.fill_create_account_passwords(password, confirmation)
        attempts = dealer.click_create_account_without_server_write()
        if attempts and password == "12345":
            pytest.xfail(
                "Development currently submits a password shorter than six "
                "characters instead of rejecting it client-side."
            )
        assert not attempts


@pytest.mark.flaky(reruns=0)
@pytest.mark.skipif(
    not DEALER_TEST_PASSWORD,
    reason="DEALER_TEST_PASSWORD is missing from .env.",
)
def test_guest_create_dealer_account_submission(page_no_login):
    dealer = _open_dealer_from_help(
        page_no_login,
        "/dealers/sign-up",
        "Create an Account",
    )
    email = _unique_email("dealer_account")
    allure.dynamic.parameter("generated_email", email)

    with allure.step("Complete both guest Dealer-account form steps"):
        dealer.fill_create_account_details(
            {**CREATE_ACCOUNT_DATA, "email": email}
        )
        dealer.open_create_account_step_two()
        dealer.fill_create_account_passwords(DEALER_TEST_PASSWORD)

    with allure.step("Create the Dealer account with valid details"):
        assert dealer.submit_create_account() == (
            "Your Dealer Account is Under Review"
        )

    with allure.step("Verify the new account can log in with the same details"):
        sign_in = page_no_login.locator("header").get_by_role(
            "link", name="Sign in"
        )
        assert sign_in.is_visible(timeout=3000)
        LoginPage(page_no_login).login(
            email=email,
            password=DEALER_TEST_PASSWORD,
            account_label="New Under Review Dealer User",
        )

    with allure.step("Verify the logged-in account remains Under Review"):
        page_no_login.goto(
            f"{BASE_URL}/dealers/sign-up",
            wait_until="domcontentloaded",
        )
        page_no_login.get_by_role(
            "heading",
            name="Your Dealer Account is Under Review",
            exact=True,
        ).wait_for(state="visible", timeout=15000)
        assert DealerPage(page_no_login).get_account_state_heading() == (
            "Your Dealer Account is Under Review"
        )


@pytest.mark.flaky(reruns=0)
@pytest.mark.skipif(
    not DEALER_TEST_PASSWORD,
    reason="DEALER_TEST_PASSWORD is missing from .env.",
)
def test_join_dealer_form_validation(eligible_dealer_user_page):
    with allure.step("Open the Join Dealer form through How to Buy"):
        dealer = _open_join_form_from_how_to_buy(eligible_dealer_user_page)

    with allure.step("Verify Join Dealer fields and locked account email"):
        assert dealer.get_join_form() == {
            "fields": [
                "full_name",
                "email",
                "phone",
                "dealership_name",
                "annual_car_imports",
                "annual_revenue",
                "position",
                "website",
            ],
            "email_disabled": True,
            "submit_enabled": True,
        }

    with allure.step("Verify missing required details do not submit"):
        join_form = eligible_dealer_user_page.get_by_role(
            "button", name="Submit", exact=True
        ).locator("xpath=ancestor::form[1]")
        join_form.locator("#full_name").fill("")
        join_form.locator("#phone").fill("")
        assert not dealer.click_join_submit_without_server_write()
        assert dealer.current_path() == "/dealers/join-as-dealer"


@pytest.mark.flaky(reruns=0)
@pytest.mark.skipif(
    not DEALER_TEST_PASSWORD,
    reason="DEALER_TEST_PASSWORD is missing from .env.",
)
def test_join_dealer_form_submission(page_no_login):
    email = _unique_email("dealer_join_account")
    allure.dynamic.parameter("generated_email", email)

    with allure.step("Create a new regular User for the Join Dealer flow"):
        LoginPage(page_no_login).register_new_user(
            email=email,
            password=DEALER_TEST_PASSWORD,
            name="Dealer Join Automation",
        )

    with allure.step("Open the Join Dealer form through How to Buy"):
        dealer = _open_join_form_from_how_to_buy(page_no_login)

    with allure.step("Submit a valid Join Dealer application"):
        dealer.fill_join_form(JOIN_DEALER_DATA)
        assert dealer.submit_join_form() == (
            "Your Dealer Account is Under Review"
        )
