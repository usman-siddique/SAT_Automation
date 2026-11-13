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
        assert how_to_pay.get_intro_text() == (
            "You can send us payments through the following payment methods."
        )

    with allure.step("Verify all six payment-method cards"):
        methods = how_to_pay.get_payment_methods()
        assert [method["heading"] for method in methods] == [
            "Bank Transfer",
            "Credit/Debit Card",
            "PayPal",
            "Cryptocurrency",
            "SAT Balance",
            "Visit Our Nearest Branch",
        ]
        assert all(method["description"] for method in methods)
        assert all(method["icon_loaded"] for method in methods)

    with allure.step("Verify sidebar destinations and active state"):
        assert how_to_pay.get_sidebar_links() == [
            {
                "label": "How to Pay",
                "path": "/how-to-pay",
                "active": True,
            },
            {
                "label": "Request Information",
                "path": "/request-vehicle-information",
                "active": False,
            },
            {
                "label": "Inquiry Form",
                "path": "/inquiry-form",
                "active": False,
            },
            {
                "label": "Bank Information",
                "path": "/bank-information",
                "active": False,
            },
        ]
