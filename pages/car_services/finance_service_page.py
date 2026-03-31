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
        # Get the iframe element
        iframe_element = self.page.locator("iframe[src*='youtube.com']")
        
        if iframe_element.count() == 0:
            raise AssertionError("YouTube iframe not found")
        
        # Get frame from element
        iframe = iframe_element.content_frame
        
        if iframe is None:
            raise AssertionError("Could not access iframe content")
        
        # Find play button inside iframe
        play_button = iframe.locator("button[aria-label='Play video']")
        
        if play_button.count() == 0:
            # Try alternative YouTube play button selector
            play_button = iframe.locator(".ytp-large-play-button")
        
        if play_button.count() == 0:
            raise AssertionError("Video play button not found in iframe")
        
        if not play_button.is_visible():
            raise AssertionError("Video play button not visible")
        
        print("✅ Video play button found")
        
        # Click play button
        play_button.click()
        print("✅ Play button clicked")
        
        # Wait 5 seconds to observe video playing
        self.page.wait_for_timeout(5000)
        print("✅ Waited 5 seconds for video to play")