import allure

from pages.help.bank_information_page import BankInformationPage
from pages.help.help_page import HelpPage


BENEFICIARY_NAME = "Shine Auto Trading Co., LTD"
BENEFICIARY_ADDRESS = (
    "156-1 HATAKENAKA AZA SHIMOGAWA IZUMIMACHI IWAKI-CITY "
    "FUKUSHIMA-PREF JAPAN"
)


def mufg(account_number):
    return {
        "Bank Name": "MUFG BANK",
        "Swift Code": "BOTKJPJT / BOTKJPJTXXX",
        "Branch Name": "Mito Branch",
        "Name": BENEFICIARY_NAME,
        "Account Number": account_number,
        "Branch Address": (
            "3-1-2-8 Izumimachi, Mito-shi, Ibaraki, Japan"
        ),
        "Beneficiary Address": BENEFICIARY_ADDRESS,
    }


def smbc(account_number="2005238"):
    return {
        "Bank Name": "SUMITOMO MITSUI BANKING CORPORATION (SMBC)",
        "Swift Code": "SMBCJPJT / SMBCJPJTXXX",
        "Branch Name": "Mito Branch",
        "Name": BENEFICIARY_NAME,
        "Account Number": account_number,
        "Branch Address": (
            "1-2-4 Miyamachi, Mito-shi, Ibaraki, Japan, MYM Building 6F"
        ),
        "Beneficiary Address": BENEFICIARY_ADDRESS,
    }


EXPECTED_BANKS = {
    "USD": [mufg("0052549"), smbc()],
    "EUR": [smbc(), mufg("0080041")],
    "JPY": [mufg("0001386"), smbc("0125157")],
    "AUD": [smbc(), mufg("0080038")],
    "GBP": [smbc(), mufg("0080067")],
    "NZD": [smbc(), mufg("0080054")],
    "CAD": [smbc(), mufg("0080070")],
    "CNY": [smbc()],
}


def test_bank_information_page(page_no_login):
    HelpPage(page_no_login).open_menu_item(
        "Bank Information",
        "/bank-information",
        ".bank-info-top-hdr:has-text('Bank Information (USD)')",
    )
    bank = BankInformationPage(page_no_login)

    with allure.step("Verify all currencies, banks, and account details"):
        actual = bank.get_bank_sections()
        assert list(actual) == list(bank.CURRENCY_SECTIONS)
        assert actual == EXPECTED_BANKS

    with allure.step("Verify every currency bank icon loads"):
        assert bank.get_currency_icon_states() == [True] * len(
            bank.CURRENCY_SECTIONS
        )
