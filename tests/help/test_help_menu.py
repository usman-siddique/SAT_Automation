import allure

from pages.help.help_page import HelpPage


def test_help_menu_items(page_no_login):
    help_page = HelpPage(page_no_login)
    expected_names = [name for name, _ in HelpPage.MENU_ITEMS]
    expected_paths = [path for _, path in HelpPage.MENU_ITEMS]

    with allure.step("Verify all Help menu items and their order"):
        assert help_page.get_menu_item_names() == expected_names

    with allure.step("Verify every Help menu destination path"):
        assert help_page.get_menu_item_paths() == expected_paths
