# ============================================================
# pages/car_services/pre_export_inspection_page.py
# Contains the PreExportInspectionPage class.
# Handles Pre Export Inspection page content verification.
# ============================================================

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class PreExportInspectionPage:
    def __init__(self, page, download_dir):
        self.page = page
        self.download_dir = download_dir


    # ============================================================
    # Verify: Main heading
    # ============================================================

    def verify_main_heading(self):
        heading = self.page.locator("h2.title:has-text('Seal The Deal With Pre-Export Inspection')")
        if not heading.is_visible():
            raise AssertionError("Main heading not visible")
        print(f"✅ Main heading verified: {heading.inner_text()}")


    # ============================================================
    # Verify: Easy Refund Policy heading
    # ============================================================

    def verify_refund_heading(self):
        heading = self.page.locator("h2.refund-title:has-text('Easy Refund Policy')")
        if not heading.is_visible():
            raise AssertionError("Refund Policy heading not visible")
        print(f"✅ Refund Policy heading verified: {heading.inner_text()}")


    # ============================================================
    # Verify: Sample Report link exists
    # ============================================================

    def verify_sample_report_link(self):
        link = self.page.locator("a[download]")
        if not link.is_visible():
            raise AssertionError("Sample Report download link not visible")
        print(f"✅ Sample Report link verified: {link.get_attribute('href')}")


    # ============================================================
    # Download: Sample Inspection Report PDF
    # ============================================================

    def download_sample_report(self):
        # Wait for download to start
        with self.page.expect_download() as download_info:
            self.page.locator("a[download]").click()
        
        download = download_info.value
        
        # Save the downloaded file
        download_path = os.path.join(self.download_dir, download.suggested_filename)
        download.save_as(download_path)
        
        print(f"✅ PDF downloaded: {download.suggested_filename}")
        
        # Verify file exists and has content
        assert os.path.exists(download_path), "Downloaded file not found"
        assert os.path.getsize(download_path) > 0, "Downloaded file is empty"
        
        print(f"✅ PDF saved to: {download_path}")
        return download_path