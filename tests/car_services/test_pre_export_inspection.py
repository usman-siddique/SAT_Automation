import allure
import pytest

from pages.car_services.car_services_page import CarServicesPage
from pages.car_services.pre_export_inspection_page import PreExportInspectionPage


@pytest.fixture
def pre_export(page_no_login, tmp_path):
    CarServicesPage(page_no_login).go_to_pre_export_inspection()
    return PreExportInspectionPage(page_no_login, str(tmp_path))


def test_pre_export_inspection_page_content(pre_export):
    with allure.step("Verify Pre-Export Inspection main heading"):
        pre_export.verify_main_heading()

    with allure.step("Verify refund-policy heading"):
        pre_export.verify_refund_heading()

    with allure.step("Verify sample-report download link"):
        pre_export.verify_sample_report_link()


def test_download_sample_inspection_report(pre_export):
    with allure.step("Download and validate the sample inspection PDF"):
        pre_export.download_sample_report()
