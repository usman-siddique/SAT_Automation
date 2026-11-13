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

    with allure.step("Verify the guide banner and main sections"):
        assert guide.get_banner_content() == {
            "title": "How to Choose the Right Used Cars",
            "description": (
                "This guide provides you with a clear picture of all major "
                "body types, so you can decide which one best suits your "
                "needs."
            ),
        }
        assert guide.get_guide_headings() == list(
            UsedCarGuidePage.MAIN_HEADINGS
        )

    with allure.step("Verify the overview and first-buyer guidance"):
        overview = guide.get_overview_content()
        assert overview["overview"].startswith(
            "This guide provides you with a clear picture"
        )
        assert (
            overview["buyer_guide_heading"]
            == "Purchase Your First Pre-Owned Vehicle – Buyer’s Guide"
        )
        assert "choosing the right body type" in overview["buyer_guide"]
        assert "passenger and cargo requirements" in overview["buyer_guide"]

    with allure.step("Verify all six used-car categories and guidance"):
        categories = guide.get_category_content()
        assert categories["headings"] == list(
            UsedCarGuidePage.CATEGORY_HEADINGS
        )
        assert len(categories["descriptions"]) == 12
        assert all(
            len(description) >= 35
            for description in categories["descriptions"]
        )

    with allure.step("Verify the purchase-purpose questions"):
        assert guide.get_purchase_questions() == list(
            UsedCarGuidePage.PURCHASE_QUESTIONS
        )

    with allure.step("Verify the closing SAT purchase guidance"):
        closing = guide.get_closing_content()
        assert (
            closing["heading"]
            == "Make the Purchase Process Convenient with SAT"
        )
        assert "explore a fantastic range of used cars" in closing[
            "description"
        ]
        assert "making your buying experience as convenient as possible" in (
            closing["description"]
        )

    with allure.step("Verify all visible guide images loaded"):
        images = guide.get_main_image_status()
        assert len(images) == 8
        assert all(image["loaded"] for image in images), images

    with allure.step("Scroll through the complete page to the footer"):
        scroll = guide.scroll_to_page_end()
        assert (
            scroll["scroll_y"] + scroll["viewport_height"]
            >= scroll["page_height"] - 5
        )
        assert scroll["footer_visible"] is True
        assert scroll["contact_heading_visible"] is True
