import allure

from pages.help.dealer_page import DealerPage
from pages.help.help_page import HelpPage


def test_become_dealer_anonymous_redirect(page_no_login):
    HelpPage(page_no_login).open_menu_item(
        "Become a SAT Japan Dealer",
        "/dealers/join-as-dealer",
        "#login_email",
        expected_final_path="/login",
    )
    dealer = DealerPage(page_no_login)

    with allure.step("Verify anonymous visitors are sent to the login page"):
        assert page_no_login.url.endswith("/login")

    with allure.step("Verify the login controls required to continue"):
        assert dealer.get_anonymous_login_controls() == {
            "email_placeholder": "Email",
            "continue_enabled": True,
        }
