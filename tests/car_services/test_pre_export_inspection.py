"""Business coverage for the SAT Pre-Export Inspection service."""

import allure
import pytest

from pages.car_services.car_services_page import CarServicesPage
from pages.car_services.pre_export_inspection_page import (
    PreExportInspectionPage,
)


@pytest.fixture
def pre_export(page_no_login, tmp_path):
    CarServicesPage(page_no_login).go_to_pre_export_inspection()
    return PreExportInspectionPage(page_no_login, tmp_path)


def test_pre_export_inspection_overview_and_refund_policy(pre_export):
    with allure.step(
        "Verify service overview, loaded banner, refund rules, and report link"
    ):
        overview = pre_export.verify_overview_and_refund_policy()
        assert overview["path"] == "/pre-export-inspection"
        assert overview["heading"] == (
            "Seal The Deal With Pre-Export Inspection"
        )
        assert overview["refund_heading"] == "Easy Refund Policy"


def test_pre_export_inspection_coverage_and_benefits(pre_export):
    with allure.step(
        "Verify all inspection coverage areas, benefits, and coverage icons"
    ):
        result = pre_export.verify_coverage_and_benefits()
        assert result == {
            "coverage": pre_export.COVERAGE_ITEMS,
            "benefits": pre_export.BENEFITS,
        }


def test_pre_export_inspection_service_process(pre_export):
    with allure.step(
        "Verify all four service steps, their guidance, and loaded icons"
    ):
        assert pre_export.verify_process_steps() == pre_export.PROCESS_STEPS


def test_pre_export_inspection_sample_report_download(pre_export):
    with allure.step(
        "Download the sample report and verify its filename, size, and PDF signature"
    ):
        report = pre_export.download_sample_report()
        assert report["filename"].lower().endswith(".pdf")
        assert report["size"] > 1000
