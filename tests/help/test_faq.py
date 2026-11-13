import time

import allure

from pages.help.faq_page import FaqPage
from pages.help.help_page import HelpPage


def open_faq(page):
    HelpPage(page).open_menu_item(
        "FAQs",
        "/faq",
        "#faq_search_input",
    )
    return FaqPage(page)


def test_faq_search_questions_and_form_validation(page_no_login):
    faq = open_faq(page_no_login)

    with allure.step("Verify FAQ search and complete question catalogue"):
        assert faq.get_faq_heading() == "Frequently Asked Questions"
        assert (
            faq.get_search_placeholder()
            == "Search a keyword or question"
        )
        assert faq.get_categories() == list(FaqPage.EXPECTED_CATEGORIES)
        assert faq.get_all_question_count() == FaqPage.EXPECTED_QUESTION_COUNT

    with allure.step("Search by answer keyword and expand the matching FAQ"):
        results = faq.search("multilingual")
        assert results["questions"] == [
            "Which languages does SAT Japan support?"
        ]
        answer = faq.expand_search_result(results["questions"][0])
        assert "supports customers in several languages" in answer

    with allure.step("Verify a missing FAQ keyword shows useful guidance"):
        results = faq.search("qa-no-such-faq-result-804655248")
        assert results["questions"] == []
        assert (
            'No FAQs found for “qa-no-such-faq-result-804655248”.'
            in results["no_results"]
        )
        assert "fill out the form below" in results["no_results"]

    with allure.step("Clear search and verify every FAQ category opens"):
        faq.search("")
        for category in FaqPage.EXPECTED_CATEGORIES:
            category_result = faq.select_category(category)
            assert category_result["active"] is True
            assert category_result["questions"], (
                f"No FAQ questions were shown for {category}."
            )

    with allure.step("Verify the Still Have Any Question form structure"):
        assert faq.get_question_form_details() == {
            "heading": "Still Have Any Question?",
            "question_required": True,
            "name_required": True,
            "email_required": True,
            "email_type": "email",
            "remember_visible": True,
            "submit_visible": True,
        }
        assert faq.check_remember_details() is True

    with allure.step("Verify empty question form fields block submission"):
        result = faq.get_question_form_validation("", "", "")
        for field_name in ("question", "name", "email"):
            assert result["fields"][field_name]["valid"] is False
            assert result["fields"][field_name]["value_missing"] is True
            assert result["fields"][field_name]["message"]
        assert result["post_count"] == 0

    with allure.step("Verify an invalid email format blocks submission"):
        result = faq.get_question_form_validation(
            "How can I get more information?",
            "SAT QA Automation",
            "invalid-email",
        )
        assert result["fields"]["question"]["valid"] is True
        assert result["fields"]["name"]["valid"] is True
        assert result["fields"]["email"]["valid"] is False
        assert result["fields"]["email"]["type_mismatch"] is True
        assert result["fields"]["email"]["message"]
        assert result["post_count"] == 0


def test_faq_question_form_successful_submission(page_no_login):
    faq = open_faq(page_no_login)
    unique_id = int(time.time())

    with allure.step("Submit a valid question from the FAQ page"):
        result = faq.submit_question(
            (
                f"Automated FAQ test question {unique_id}. "
                "Please ignore."
            ),
            "SAT QA Automation",
            f"sat.qa.faq.{unique_id}@gmail.com",
        )

    with allure.step("Verify the question was accepted"):
        assert result["status"] == 302
        assert result["navigation_status"] == 200
        assert result["url"].endswith("/faq")
