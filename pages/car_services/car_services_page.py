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
        
     
    # ============================================================
    # Navigation: Hover Car Services menu, click Car Carrier Service
    # ============================================================   
        
    def go_to_car_carrier_service(self):
        self.page.locator("p.cnm-cls", has_text="Car Services").hover()
        self.page.wait_for_timeout(500)
        self.page.get_by_role("link", name="Car Carrier Service", exact=True).click()
        self.page.wait_for_url("**/car-carrier")
        self.page.locator("h2.carrier-policy-comman-hdr:has-text('Delivery Options')").wait_for(state="visible")
        print("✅ Navigation to Car Carrier Service: PASS")
        
      
    # ============================================================
    # Navigation: Hover Car Services menu, click Customs Clearance
    # ============================================================  
        
    def go_to_customs_clearance(self):
        self.page.locator("p.cnm-cls", has_text="Car Services").hover()
        self.page.wait_for_timeout(500)
        self.page.get_by_role("link", name="Custom Clearance", exact=True).click()
        self.page.wait_for_url("**/customs-clearance")
        self.page.locator("h1.text:has-text('Ensure Fast and Compliant Shipments')").wait_for(state="visible")
        print("✅ Navigation to Customs Clearance: PASS")
        
        
     
    # ============================================================
    # Navigation: Hover Car Services menu, click Pre Export Inspection
    # ============================================================   
    
    def go_to_pre_export_inspection(self):
        self.page.locator("p.cnm-cls", has_text="Car Services").hover()
        self.page.wait_for_timeout(500)
        self.page.get_by_role("link", name="Pre Export Inspection", exact=True).click()
        self.page.wait_for_url("**/pre-export-inspection")
        self.page.locator("h2.title:has-text('Seal The Deal With Pre-Export Inspection')").wait_for(state="visible")
        print("✅ Navigation to Pre Export Inspection: PASS")
        
        
        
    # ============================================================
    # Navigation: Hover Car Services menu, click Marine Insurance Service
    # ============================================================
    
    def go_to_marine_insurance(self):
        self.page.locator("p.cnm-cls", has_text="Car Services").hover()
        self.page.wait_for_timeout(500)
        self.page.get_by_role("link", name="Marine Insurance Service", exact=True).click()
        self.page.wait_for_url("**/marine-insurance-services")
        self.page.locator("img.banner-marine-insurance").wait_for(state="visible")
        print("✅ Navigation to Marine Insurance Service: PASS")
        
        
    # ============================================================
    # Navigation: Hover Car Services menu, click Non Stolen Vehicle Check
    # ============================================================   
    def go_to_non_stolen_vehicle(self):
        self.page.locator("p.cnm-cls", has_text="Car Services").hover()
        link = self.page.get_by_role("link", name="Non Stolen Vehicle Check", exact=True)
        link.wait_for(state="visible")  # Wait for menu to fully open before clicking
        link.click()
        self.page.wait_for_url("**/non-stolen-vehicle", wait_until="domcontentloaded")
        print("✅ Navigation to Non Stolen Vehicle: PASS")