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

    def get_main_heading(self):
        heading = self.page.locator("h2.text:has-text('Secure Storage Service For Your Vehicle')")
        heading.wait_for(state="visible")
        return heading.inner_text().strip()


    # ============================================================
    # Verify: Countries section heading
    # ============================================================

    def get_countries_heading(self):
        heading = self.page.locator("h2.offer-services-hdr:has-text('Countries Where We Offer Storage Service')")
        heading.wait_for(state="visible")
        return heading.inner_text().strip()


    # ============================================================
    # Verify: Benefits section heading
    # ============================================================

    def get_benefits_heading(self):
        heading = self.page.locator("h1.compmany-hdr:has-text('Benefits of SAT Vehicle Storage Service')")
        heading.wait_for(state="visible")
        return heading.inner_text().strip()


    # ============================================================
    # Verify: Why Store heading
    # ============================================================

    def get_why_store_heading(self):
        heading = self.page.locator("h2.compmany-hdr:has-text('Why Store a New Vehicle?')")
        heading.wait_for(state="visible")
        return heading.inner_text().strip()
