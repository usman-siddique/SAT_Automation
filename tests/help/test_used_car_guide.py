import allure

from pages.help.help_page import HelpPage
from pages.help.used_car_guide_page import UsedCarGuidePage


def test_used_car_guide_page(page_no_login):
    HelpPage(page_no_login).open_menu_item(
        "How to Pick the Right Used Car",
        "/how-to-choose",
        "h2:has-text('Overview')",
    )
    guide = UsedCarGuidePage(page_no_login)

    with allure.step("Verify the main used-car guide sections"):
        assert guide.get_guide_headings() == [
            "Overview",
            "Choose a Used Car by Category",
            "Determine the Purpose of Purchase",
            "Make the Purchase Process Convenient with SAT",
        ]
