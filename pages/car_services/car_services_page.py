# ============================================================
# pages/car_services/car_services_page.py
# Contains the CarServicesPage class.
# Handles Car Services hover menu navigation with retry logic.
# run: pytest tests/car_services/ -v -s
# ============================================================

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class CarServicesPage:
    def __init__(self, page):
        self.page = page


    # ============================================================
    # Helper: Retry wrapper for navigation methods
    # ============================================================

    def _retry_navigation(self, nav_func, max_retries=2):
        """Retry navigation up to max_retries times if it fails"""
        for attempt in range(max_retries):
            try:
                nav_func()
                return
            except Exception as e:
                if attempt == max_retries - 1:
                    raise
                print(f"⚠️ Navigation attempt {attempt + 1} failed, retrying...")
                self.page.wait_for_timeout(1000)


    # ============================================================
    # Navigation: Hover Car Services menu, click Auction Service
    # ============================================================

    def go_to_auction_service(self):
        def _nav():
            self.page.locator("p.cnm-cls", has_text="Car Services").hover()
            self.page.locator("p.cnm-cls", has_text="Car Services").locator("..").locator("div.dropdown_content_header").wait_for(state="visible")
            self.page.get_by_role("link", name="Auction Service").click()
            self.page.wait_for_url("**/sat-auction", timeout=10000)
            self.page.get_by_text("Auction Service Overview").wait_for(state="visible")
            print("✅ Navigation to Auction Service: PASS")
        
        self._retry_navigation(_nav)


    # ============================================================
    # Navigation: Hover Car Services menu, click Shipping Schedule
    # ============================================================

    def go_to_shipping_schedule(self):
        def _nav():
            self.page.locator("p.cnm-cls", has_text="Car Services").hover()
            self.page.wait_for_timeout(500)
            self.page.get_by_role("link", name="Shipping Schedule").click()
            self.page.wait_for_url("**/shipping-schedule", timeout=10000)
            self.page.locator("p.see-first-para").wait_for(state="visible")
            print("✅ Navigation to Shipping Schedule: PASS")
        
        self._retry_navigation(_nav)


    # ============================================================
    # Navigation: Hover Car Services menu, click Insurance Services
    # ============================================================

    def go_to_insurance_services(self):
        def _nav():
            self.page.locator("p.cnm-cls", has_text="Car Services").hover()
            self.page.wait_for_timeout(500)
            self.page.get_by_role("link", name="Insurance Service", exact=True).click()
            self.page.wait_for_url("**/insurance-services", timeout=10000)
            self.page.locator("h1.insurance-bannar-title").wait_for(state="visible")
            print("✅ Navigation to Insurance Services: PASS")
        
        self._retry_navigation(_nav)


    # ============================================================
    # Navigation: Hover Car Services menu, click Storage Service
    # ============================================================

    def go_to_storage_service(self):
        def _nav():
            self.page.locator("p.cnm-cls", has_text="Car Services").hover()
            self.page.wait_for_timeout(500)
            self.page.get_by_role("link", name="Storage Service", exact=True).click()
            self.page.wait_for_url("**/storage-policy", timeout=10000)
            self.page.locator("h2.text:has-text('Secure Storage Service')").wait_for(state="visible")
            print("✅ Navigation to Storage Service: PASS")
        
        self._retry_navigation(_nav)


    # ============================================================
    # Navigation: Hover Car Services menu, click Finance Service
    # ============================================================

    def go_to_finance_service(self):
        def _nav():
            self.page.locator("p.cnm-cls", has_text="Car Services").hover()
            self.page.wait_for_timeout(500)
            self.page.get_by_role("link", name="Finance Service", exact=True).click()
            self.page.wait_for_url("**/finance-services", timeout=10000)
            self.page.locator("img.banner-finance-services").wait_for(state="visible")
            print("✅ Navigation to Finance Service: PASS")
        
        self._retry_navigation(_nav)


    # ============================================================
    # Navigation: Hover Car Services menu, click Car Carrier Service
    # ============================================================

    def go_to_car_carrier_service(self):
        def _nav():
            self.page.locator("p.cnm-cls", has_text="Car Services").hover()
            self.page.wait_for_timeout(500)
            self.page.get_by_role("link", name="Car Carrier Service", exact=True).click()
            self.page.wait_for_url("**/car-carrier", timeout=10000)
            self.page.locator("h2.carrier-policy-comman-hdr:has-text('Delivery Options')").wait_for(state="visible")
            print("✅ Navigation to Car Carrier Service: PASS")
        
        self._retry_navigation(_nav)


    # ============================================================
    # Navigation: Hover Car Services menu, click Customs Clearance
    # ============================================================

    def go_to_customs_clearance(self):
        def _nav():
            self.page.locator("p.cnm-cls", has_text="Car Services").hover()
            self.page.wait_for_timeout(500)
            self.page.get_by_role("link", name="Custom Clearance", exact=True).click()
            self.page.wait_for_url("**/customs-clearance", timeout=10000)
            self.page.locator("h1.text:has-text('Ensure Fast and Compliant Shipments')").wait_for(state="visible")
            print("✅ Navigation to Customs Clearance: PASS")
        
        self._retry_navigation(_nav)


    # ============================================================
    # Navigation: Hover Car Services menu, click Pre Export Inspection
    # ============================================================

    def go_to_pre_export_inspection(self):
        def _nav():
            self.page.locator("p.cnm-cls", has_text="Car Services").hover()
            self.page.wait_for_timeout(500)
            self.page.get_by_role("link", name="Pre Export Inspection", exact=True).click()
            self.page.wait_for_url("**/pre-export-inspection", timeout=10000)
            self.page.locator("h2.title:has-text('Seal The Deal With Pre-Export Inspection')").wait_for(state="visible")
            print("✅ Navigation to Pre Export Inspection: PASS")
        
        self._retry_navigation(_nav)


    # ============================================================
    # Navigation: Hover Car Services menu, click Marine Insurance Service
    # ============================================================

    def go_to_marine_insurance(self):
        def _nav():
            self.page.locator("p.cnm-cls", has_text="Car Services").hover()
            self.page.wait_for_timeout(500)
            self.page.get_by_role("link", name="Marine Insurance Service", exact=True).click()
            self.page.wait_for_url("**/marine-insurance-services", timeout=10000)
            self.page.locator("img.banner-marine-insurance").wait_for(state="visible")
            print("✅ Navigation to Marine Insurance Service: PASS")
        
        self._retry_navigation(_nav)


    # ============================================================
    # Navigation: Hover Car Services menu, click Non Stolen Vehicle Check
    # ============================================================

    def go_to_non_stolen_vehicle(self):
        def _nav():
            self.page.locator("p.cnm-cls", has_text="Car Services").hover()
            link = self.page.get_by_role("link", name="Non Stolen Vehicle Check", exact=True)
            link.wait_for(state="visible")
            link.click()
            self.page.wait_for_url("**/non-stolen-vehicle", wait_until="domcontentloaded", timeout=10000)
            print("✅ Navigation to Non Stolen Vehicle: PASS")
        
        self._retry_navigation(_nav)