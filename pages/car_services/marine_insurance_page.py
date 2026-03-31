# ============================================================
# pages/car_services/marine_insurance_page.py
# Contains the MarineInsurancePage class.
# Handles Marine Insurance Service page content verification.
# ============================================================

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class MarineInsurancePage:
    def __init__(self, page):
        self.page = page


    # ============================================================
    # Verify: Banner image is visible
    # ============================================================

    def verify_banner_image(self):
        banner = self.page.locator("img.banner-marine-insurance")
        if not banner.is_visible():
            raise AssertionError("Marine Insurance banner image not visible")
        print(f"✅ Banner image verified: {banner.get_attribute('alt')}")


    # ============================================================
    # Verify: What Our Service Covers heading
    # ============================================================

    def verify_coverage_heading(self):
        heading = self.page.locator("h2.marine-insurance-comman-hdr:has-text('What Our Service Covers')")
        if not heading.is_visible():
            raise AssertionError("'What Our Service Covers' heading not visible")
        print(f"✅ Coverage heading verified: {heading.inner_text()}")


    # ============================================================
    # Verify: Steps heading
    # ============================================================

    def verify_steps_heading(self):
        heading = self.page.locator("h2.marine-insurance-comman-hdr:has-text('Steps to Utilize Our Marine Insurance Service')")
        if not heading.is_visible():
            raise AssertionError("Steps heading not visible")
        print(f"✅ Steps heading verified: {heading.inner_text()}")