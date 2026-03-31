# ============================================================
# pages/car_services/car_carrier_page.py
# Contains the CarCarrierPage class.
# Handles Car Carrier Service page content verification.
# ============================================================

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class CarCarrierPage:
    def __init__(self, page):
        self.page = page


    # ============================================================
    # Verify: Delivery Options heading
    # ============================================================

    def verify_delivery_options_heading(self):
        heading = self.page.locator("h2.carrier-policy-comman-hdr:has-text('Delivery Options')")
        if not heading.is_visible():
            raise AssertionError("Delivery Options heading not visible")
        print(f"✅ Delivery Options heading verified: {heading.inner_text()}")


    # ============================================================
    # Verify: Benefits heading
    # ============================================================

    def verify_benefits_heading(self):
        heading = self.page.locator("h2.carrier-policy-comman-hdr:has-text('Benefits of Our Carrier Service')")
        if not heading.is_visible():
            raise AssertionError("Benefits heading not visible")
        print(f"✅ Benefits heading verified: {heading.inner_text()}")


    # ============================================================
    # Verify: Both images are visible
    # ============================================================

    def verify_images(self):
        img1 = self.page.locator("img.carrier-card-img[alt='']")
        if img1.count() > 0:
            if img1.first.is_visible():
                print("✅ First carrier image verified")
        else:
            raise AssertionError("First carrier image not found")
        
        img2 = self.page.locator("img.carrier-card-img").nth(1)
        if img2.is_visible():
            print("✅ Second carrier image verified")
        else:
            raise AssertionError("Second carrier image not visible")