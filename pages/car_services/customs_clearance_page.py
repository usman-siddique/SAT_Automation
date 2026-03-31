# ============================================================
# pages/car_services/customs_clearance_page.py
# Contains the CustomsClearancePage class.
# Handles Customs Clearance page content verification.
# ============================================================

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class CustomsClearancePage:
    def __init__(self, page):
        self.page = page


    # ============================================================
    # Verify: Main heading
    # ============================================================

    def verify_main_heading(self):
        heading = self.page.locator("h1.text:has-text('Ensure Fast and Compliant Shipments')")
        if not heading.is_visible():
            raise AssertionError("Main heading not visible")
        print(f"✅ Main heading verified: {heading.inner_text()}")


    # ============================================================
    # Verify: Image is visible
    # ============================================================

    def verify_image(self):
        img = self.page.locator("img.finance-body-img")
        if not img.is_visible():
            raise AssertionError("Customs clearance image not visible")
        print("✅ Customs clearance image verified")


    # ============================================================
    # Verify: Steps heading
    # ============================================================

    def verify_steps_heading(self):
        heading = self.page.locator("h2.finance-services-comman-hdr:has-text('Steps to Utilize Our Customs Clearance Service')")
        if not heading.is_visible():
            raise AssertionError("Steps heading not visible")
        print(f"✅ Steps heading verified: {heading.inner_text()}")