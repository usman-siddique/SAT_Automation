# ============================================================
# pages/car_services/storage_service_page.py
# Contains the StorageServicePage class.
# Handles Storage Service page content verification.
# ============================================================

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class StorageServicePage:
    def __init__(self, page):
        self.page = page


    # ============================================================
    # Verify: Main heading is visible
    # ============================================================

    def verify_main_heading(self):
        heading = self.page.locator("h2.text:has-text('Secure Storage Service For Your Vehicle')")
        if not heading.is_visible():
            raise AssertionError("Main heading not visible")
        print(f"✅ Main heading verified: {heading.inner_text()}")


    # ============================================================
    # Verify: Countries section heading
    # ============================================================

    def verify_countries_heading(self):
        heading = self.page.locator("h2.offer-services-hdr:has-text('Countries Where We Offer Storage Service')")
        if not heading.is_visible():
            raise AssertionError("Countries section heading not visible")
        print(f"✅ Countries section verified: {heading.inner_text()}")


    # ============================================================
    # Verify: Benefits section heading
    # ============================================================

    def verify_benefits_heading(self):
        heading = self.page.locator("h1.compmany-hdr:has-text('Benefits of SAT Vehicle Storage Service')")
        if not heading.is_visible():
            raise AssertionError("Benefits section heading not visible")
        print(f"✅ Benefits section verified: {heading.inner_text()}")


    # ============================================================
    # Verify: Why Store heading
    # ============================================================

    def verify_why_store_heading(self):
        heading = self.page.locator("h2.compmany-hdr:has-text('Why Store a New Vehicle?')")
        if not heading.is_visible():
            raise AssertionError("Why Store heading not visible")
        print(f"✅ Why Store section verified: {heading.inner_text()}")