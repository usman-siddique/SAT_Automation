import allure

from pages.help.faq_page import FaqPage
from pages.help.help_page import HelpPage


def test_faq_page(page_no_login):
    HelpPage(page_no_login).open_menu_item(
        "FAQ’s",
        "/faq",
        "button[data-bs-toggle='collapse']",
    )
    faq = FaqPage(page_no_login)

    with allure.step("Verify FAQ questions are available"):
        questions = faq.get_questions()
        assert len(questions) >= 8
        assert questions[0] == "Can I become a registered member of SAT ?"

    with allure.step("Expand the first FAQ and verify its answer"):
        question, answer = faq.expand_first_question()
        assert question == "Can I become a registered member of SAT ?"
        assert "registered member of SAT" in answer


def test_faq_question_form_empty_required_fields(page_no_login):
    HelpPage(page_no_login).open_menu_item(
        "FAQ’s",
        "/faq",
        "button[data-bs-toggle='collapse']",
    )
    faq = FaqPage(page_no_login)

    with allure.step("Check the empty required FAQ question fields"):
        messages = faq.get_empty_question_form_validation_messages()
        assert set(messages) == {"question", "name", "email"}
        assert all(messages.values())
