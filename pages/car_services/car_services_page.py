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
        
    # ============================================================
    # Navigation: Hover Car Services menu, click Insurance Services
    # ============================================================          
    def go_to_insurance_services(self):
        self.page.locator("p.cnm-cls", has_text="Car Services").hover()
        self.page.wait_for_timeout(500)
        # Use exact text match to avoid Marine Insurance Service
        self.page.get_by_role("link", name="Insurance Service", exact=True).click()
        self.page.wait_for_url("**/insurance-services")
        self.page.locator("h1.insurance-bannar-title").wait_for(state="visible")
        print("✅ Navigation to Insurance Services: PASS")
        
        
    # ============================================================
    # Navigation: Hover Car Services menu, click Storage Service    
    # ============================================================
        
    def go_to_storage_service(self):
        self.page.locator("p.cnm-cls", has_text="Car Services").hover()
        self.page.wait_for_timeout(500)
        self.page.get_by_role("link", name="Storage Service", exact=True).click()
        self.page.wait_for_url("**/storage-policy")
        self.page.locator("h2.text:has-text('Secure Storage Service')").wait_for(state="visible")
        print("✅ Navigation to Storage Service: PASS")
   
   
    # ============================================================   
    # Navigation: Hover Car Services menu, click Finance Service
    # ============================================================  
        
    def go_to_finance_service(self):
        self.page.locator("p.cnm-cls", has_text="Car Services").hover()
        self.page.wait_for_timeout(500)  # Wait for dropdown to stabilize
        self.page.get_by_role("link", name="Finance Service", exact=True).click()
        self.page.wait_for_url("**/finance-services")
        self.page.locator("img.banner-finance-services").wait_for(state="visible")
        print("✅ Navigation to Finance Service: PASS")