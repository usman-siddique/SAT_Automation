import pytest

from pages.car_services.car_services_page import CarServicesPage
from pages.car_services.finance_service_page import FinanceServicePage


@pytest.fixture
def finance(page_no_login):
    CarServicesPage(page_no_login).go_to_finance_service()
    return FinanceServicePage(page_no_login)


class TestFinanceService:
    def test_banner_image(self, finance):
        finance.verify_banner_image()

    def test_main_heading(self, finance):
        finance.verify_main_heading()

    def test_video_playback(self, finance):
        finance.verify_and_play_video()
