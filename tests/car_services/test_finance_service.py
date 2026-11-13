"""Business coverage for the SAT Finance Service page."""

import allure

from pages.car_services.car_services_page import CarServicesPage
from pages.car_services.finance_service_page import FinanceServicePage


def open_finance_service(page):
    CarServicesPage(page).go_to_finance_service()
    return FinanceServicePage(page)


def test_finance_service_overview_banner_and_video(page_no_login):
    finance = open_finance_service(page_no_login)

    with allure.step("Verify page overview, headings, and loaded banner"):
        overview = finance.verify_overview()
        assert overview["path"] == "/finance-services"
        assert overview["hero_heading"].startswith("Enjoy flexible")
        assert overview["main_heading"] == "Pay With Easy Installments"

    with allure.step("Verify the Finance Service YouTube embed contract"):
        assert "/embed/" in finance.verify_video_embed()


def test_finance_service_process_and_payment_plan(page_no_login):
    finance = open_finance_service(page_no_login)

    with allure.step("Verify all four finance steps and their guidance"):
        assert finance.verify_finance_process() == finance.PROCESS_STEPS


def test_finance_service_benefits(page_no_login):
    finance = open_finance_service(page_no_login)

    with allure.step("Verify all four Finance Service benefits and images"):
        assert finance.verify_finance_benefits() == finance.BENEFITS
