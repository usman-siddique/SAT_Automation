# ============================================================
# pages/car_services/car_services_page.py
# Contains the CarServicesPage class.
# Handles only the Car Services hover menu navigation.
# Reused by all Car Services sub-pages.
# ============================================================

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


# ============================================================
# Page Class: Car Services Page
# ============================================================

class CarServicesPage:
    def __init__(self, page):
        self.page = page


    # ============================================================
    # Navigation: Hover Car Services menu, click Auction Service
    # ============================================================

    def go_to_auction_service(self):
        self.page.locator("p.cnm-cls", has_text="Car Services").hover()

        self.page.locator("p.cnm-cls", has_text="Car Services").locator("..").locator("div.dropdown_content_header").wait_for(state="visible")

        self.page.get_by_role("link", name="Auction Service").click()
        self.page.wait_for_url("**/sat-auction")

        self.page.get_by_text("Auction Service Overview").wait_for(state="visible")

        print("✅ Navigation to Auction Service: PASS")