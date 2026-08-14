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
        images = self.page.locator("img.carrier-card-img")
        assert images.count() >= 2, "Expected at least two carrier images"

        for index in range(2):
            image = images.nth(index)
            image.scroll_into_view_if_needed()
            image.wait_for(state="visible")
            self.page.wait_for_function(
                "(img) => img.complete && img.naturalWidth > 0",
                arg=image.element_handle(),
                timeout=10000,
            )
            print(f"✅ Carrier image {index + 1} verified")
