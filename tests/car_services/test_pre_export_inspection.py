import pytest

from pages.car_services.car_services_page import CarServicesPage
from pages.car_services.pre_export_inspection_page import PreExportInspectionPage


@pytest.fixture
def pre_export(page_no_login, tmp_path):
    CarServicesPage(page_no_login).go_to_pre_export_inspection()
    return PreExportInspectionPage(page_no_login, str(tmp_path))


class TestPreExportInspection:
    def test_main_heading(self, pre_export):
        pre_export.verify_main_heading()

    def test_refund_heading(self, pre_export):
        pre_export.verify_refund_heading()

    def test_sample_report_link(self, pre_export):
        pre_export.verify_sample_report_link()

    def test_download_sample_report(self, pre_export):
        pre_export.download_sample_report()
