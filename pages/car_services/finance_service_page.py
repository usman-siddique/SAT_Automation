# ============================================================
# pages/car_services/finance_service_page.py
# Contains the FinanceServicePage class.
# Handles Finance Service page content verification.
# ============================================================

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class FinanceServicePage:
    def __init__(self, page):
        self.page = page


    # ============================================================
    # Verify: Banner image is visible
    # ============================================================

    def verify_banner_image(self):
        banner = self.page.locator("img.banner-finance-services")
        if not banner.is_visible():
            raise AssertionError("Finance service banner image not visible")
        print(f"✅ Banner image verified: {banner.get_attribute('alt')}")


    # ============================================================
    # Verify: Main heading is visible
    # ============================================================

    def verify_main_heading(self):
        heading = self.page.locator("h1.title:has-text('Pay With Easy Installments')")
        if not heading.is_visible():
            raise AssertionError("Main heading not visible")
        print(f"✅ Main heading verified: {heading.inner_text()}")


    # ============================================================
    # Verify: Video exists, click play button, wait 5 seconds
    # ============================================================

    def verify_and_play_video(self):
        iframe_element = self.page.locator("iframe[src*='youtube.com']")
        iframe_element.wait_for(state="visible")

        iframe = iframe_element.content_frame

        if iframe is None:
            raise AssertionError("Could not access iframe content")

        play_button = iframe.locator(".ytp-large-play-button")
        play_button.wait_for(state="visible")
        play_button.click()

        print("✅ Video play button clicked")