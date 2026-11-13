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

    with allure.step("Verify the Safety with SAT banner"):
        assert guide.get_banner() == {
            "title": "BUY VEHICLES SAFELY WITH SAT",
            "image_alt": "Buy Vehicles Safely with SAT",
        }

    with allure.step("Verify all fraud-prevention guidance sections"):
        content = guide.get_main_section_content()
        assert content == {
            "detail": "Detail",
            "fraud_heading": "How to Beware Of Fraudulent Activities",
            "fraud_guidance": list(SafeBuyingGuidePage.FRAUD_GUIDANCE),
            "safe_heading": "Staying Safe the SAT Way",
        }

    with allure.step("Verify both safety tab labels and targets"):
        assert guide.get_tabs() == [
            {
                "label": "Buying Check-List",
                "target": "#my-reviews",
                "selected": "true",
            },
            {
                "label": "Online Safety",
                "target": "#add-review",
                "selected": "false",
            },
        ]

    with allure.step("Verify every Buying Check-List item"):
        buying = guide.select_tab("Buying Check-List")
        assert buying["selected"] == "true"
        assert buying["active"] is True
        assert buying["panel_visible"] is True
        assert buying["headings"] == list(SafeBuyingGuidePage.BUYING_CHECKS)
        assert len(buying["descriptions"]) == 6
        assert all(len(text) >= 50 for text in buying["descriptions"])

    with allure.step("Switch tabs and verify every Online Safety item"):
        online = guide.select_tab("Online Safety")
        assert online["selected"] == "true"
        assert online["active"] is True
        assert online["panel_visible"] is True
        assert online["headings"] == list(
            SafeBuyingGuidePage.ONLINE_SAFETY_CHECKS
        )
        assert len(online["descriptions"]) == 4
        assert all(len(text) >= 50 for text in online["descriptions"])

    with allure.step("Switch back to Buying Check-List"):
        buying = guide.select_tab("Buying Check-List")
        assert buying["selected"] == "true"
        assert buying["active"] is True
        assert buying["panel_visible"] is True
        assert buying["headings"] == list(SafeBuyingGuidePage.BUYING_CHECKS)

    with allure.step("Verify all vehicle-check offer cards"):
        checks = guide.get_vehicle_checks()
        assert checks["heading"] == "What Our Vehicle Checks Offer"
        assert checks["cards"] == list(SafeBuyingGuidePage.VEHICLE_CHECKS)
        assert len(checks["descriptions"]) == 3
        assert all(len(text) >= 50 for text in checks["descriptions"])

    with allure.step("Verify the banner and vehicle-check images loaded"):
        images = guide.get_image_status()
        assert len(images) == 4
        assert all(image["loaded"] for image in images), images
