# ============================================================
# pages/car_services/car_services_page.py
# Contains the CarServicesPage class.
# Handles Car Services hover menu navigation.
# ============================================================

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


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
        

    # ============================================================
    # Navigation: Hover Car Services menu, click Shipping Schedule
    # ============================================================

    def go_to_shipping_schedule(self):
        self.page.locator("p.cnm-cls", has_text="Car Services").hover()
        self.page.wait_for_timeout(500)
        self.page.get_by_role("link", name="Shipping Schedule").click()
        self.page.wait_for_url("**/shipping-schedule")
        self.page.locator("p.see-first-para").wait_for(state="visible")
        print("✅ Navigation to Shipping Schedule: PASS")