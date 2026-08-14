import allure
import pytest

from pages.car_services.car_services_page import CarServicesPage
from pages.car_services.finance_service_page import FinanceServicePage


@pytest.fixture
def finance(page_no_login):
    CarServicesPage(page_no_login).go_to_finance_service()
    return FinanceServicePage(page_no_login)


def test_finance_service_page_content(finance):
    with allure.step("Verify Finance Service banner"):
        finance.verify_banner_image()

    with allure.step("Verify Finance Service main heading"):
        finance.verify_main_heading()

    with allure.step("Verify Finance Service YouTube video embed"):
        finance.verify_video_embed()
