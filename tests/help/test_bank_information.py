import allure

from pages.help.bank_information_page import BankInformationPage
from pages.help.help_page import HelpPage


def test_bank_information_page(page_no_login):
    HelpPage(page_no_login).open_menu_item(
        "Bank Information",
        "/bank-information",
        "h2:has-text('Bank Information (USD)')",
    )
    bank = BankInformationPage(page_no_login)

    with allure.step("Verify every supported bank currency section"):
        assert bank.get_currency_sections() == list(bank.CURRENCY_SECTIONS)

    with allure.step("Verify the required bank-information labels"):
        assert bank.get_detail_labels() == [
            "Bank Name:",
            "Swift Code:",
            "Branch Name:",
            "Account Number:",
        ]
