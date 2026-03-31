# ============================================================
# tests/car_services/test_pre_export_inspection.py
#
# HOW TO RUN:
#   pytest tests/car_services/test_pre_export_inspection.py -v -s
# ============================================================

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
import tempfile

from pages.car_services.car_services_page import CarServicesPage
from pages.car_services.pre_export_inspection_page import PreExportInspectionPage


def setup_pre_export_page(page_no_login):
    # Create temporary directory for downloads
    download_dir = tempfile.mkdtemp()
    CarServicesPage(page_no_login).go_to_pre_export_inspection()
    return PreExportInspectionPage(page_no_login, download_dir)


# ============================================================
# Test: Verify all Pre Export Inspection page elements and download
# ============================================================

def test_pre_export_inspection_all(page_no_login):
    print("\n" + "="*60)
    print("✅ PRE EXPORT INSPECTION - COMPLETE VERIFICATION")
    print("="*60)
    
    pre_export = setup_pre_export_page(page_no_login)
    
    # Verify all elements on single page
    pre_export.verify_main_heading()
    pre_export.verify_refund_heading()
    pre_export.verify_sample_report_link()
    
    # Download and verify PDF
    pre_export.download_sample_report()
    
    print("\n✅ PRE EXPORT INSPECTION COMPLETE")