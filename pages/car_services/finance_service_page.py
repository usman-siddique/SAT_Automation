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
    # Verify: Stable YouTube embed contract
    # ============================================================

    def verify_video_embed(self):
        video = self.page.locator("iframe[title='YouTube video player']")
        video.wait_for(state="visible")

        source = video.get_attribute("src") or ""
        valid_embed_hosts = (
            "youtube.com/embed/",
            "youtube-nocookie.com/embed/",
        )
        assert any(host in source for host in valid_embed_hosts), (
            f"Finance video has an unexpected embed URL: {source}"
        )

        print(f"✅ Finance video embed verified: {source}")
