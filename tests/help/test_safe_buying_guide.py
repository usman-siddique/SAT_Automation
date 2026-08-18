import allure

from pages.help.help_page import HelpPage
from pages.help.safe_buying_guide_page import SafeBuyingGuidePage


def test_safe_buying_guide_page(page_no_login):
    HelpPage(page_no_login).open_menu_item(
        "Buying Vehicles Safely Guide",
        "/safety-with-sat",
        "text=How to Beware Of Fraudulent Activities",
    )
    guide = SafeBuyingGuidePage(page_no_login)

    with allure.step("Verify the main vehicle-safety guide sections"):
        assert guide.get_safety_sections() == [
            "How to Beware Of Fraudulent Activities",
            "Cyber Safety Precaution",
            "Staying Safe the SAT Way",
            "What Our Vehicle Checks Offer",
        ]
