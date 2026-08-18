import allure

from pages.help.help_page import HelpPage
from pages.help.how_to_pay_page import HowToPayPage


def test_how_to_pay_page(page_no_login):
    HelpPage(page_no_login).open_menu_item(
        "How to Pay",
        "/how-to-pay",
        "h1:has-text('How to Pay')",
    )
    how_to_pay = HowToPayPage(page_no_login)

    with allure.step("Verify the How to Pay heading"):
        assert how_to_pay.get_main_heading() == "How to Pay"

    with allure.step("Verify all payment-method sections"):
        assert how_to_pay.get_payment_method_headings() == [
            "Bank Transfer",
            "Credit/Debit Card",
            "PayPal",
            "Visit Our Nearest Branch",
        ]
