# ============================================================
# pages/car_services/car_services_page.py
# Contains the CarServicesPage class.
# Handles Car Services hover menu navigation with proper waits.
# run: pytest tests/car_services/ -v -s
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
        link = self.page.get_by_role("link", name="Auction Service")
        link.wait_for(state="visible")
        link.click()
        self.page.get_by_text("Auction Service Overview").wait_for(state="visible")
        print("✅ Navigation to Auction Service: PASS")


    # ============================================================
    # Navigation: Hover Car Services menu, click Shipping Schedule
    # ============================================================

    def go_to_shipping_schedule(self):
        self.page.locator("p.cnm-cls", has_text="Car Services").hover()
        link = self.page.get_by_role("link", name="Shipping Schedule")
        link.wait_for(state="visible")
        link.click()
        self.page.locator("p.see-first-para").wait_for(state="visible")
        print("✅ Navigation to Shipping Schedule: PASS")


    # ============================================================
    # Navigation: Hover Car Services menu, click Warranty Service
    # ============================================================

    def go_to_warranty_service(self):
        self.page.locator("p.cnm-cls", has_text="Car Services").hover()
        link = self.page.get_by_role("link", name="Warranty Service", exact=True)
        link.wait_for(state="visible")
        link.click()
        self.page.wait_for_url("**/sat-warranty")
        self.page.get_by_role("heading", name="SAT Japan Warranty", exact=True).wait_for(state="visible")
        print("✅ Navigation to Warranty Service: PASS")


    # ============================================================
    # Navigation: Hover Car Services menu, click Storage Service
    # ============================================================

    def go_to_storage_service(self):
        self.page.locator("p.cnm-cls", has_text="Car Services").hover()
        link = self.page.get_by_role("link", name="Storage Service", exact=True)
        link.wait_for(state="visible")
        link.click()
        self.page.locator("h2.text:has-text('Secure Storage Service')").wait_for(state="visible")
        print("✅ Navigation to Storage Service: PASS")


    # ============================================================
    # Navigation: Hover Car Services menu, click Finance Service
    # ============================================================

    def go_to_finance_service(self):
        self.page.locator("p.cnm-cls", has_text="Car Services").hover()
        link = self.page.get_by_role("link", name="Finance Service", exact=True)
        link.wait_for(state="visible")
        link.click()
        self.page.locator("img.banner-finance-services").wait_for(state="visible")
        print("✅ Navigation to Finance Service: PASS")


    # ============================================================
    # Navigation: Hover Car Services menu, click Car Carrier Service
    # ============================================================

    def go_to_car_carrier_service(self):
        self.page.locator("p.cnm-cls", has_text="Car Services").hover()
        link = self.page.get_by_role("link", name="Car Carrier Service", exact=True)
        link.wait_for(state="visible")
        link.click()
        self.page.locator("h2.carrier-policy-comman-hdr:has-text('Delivery Options')").wait_for(state="visible")
        print("✅ Navigation to Car Carrier Service: PASS")


    # ============================================================
    # Navigation: Hover Car Services menu, click Customs Clearance
    # ============================================================

    def go_to_customs_clearance(self):
        self.page.locator("p.cnm-cls", has_text="Car Services").hover()
        link = self.page.get_by_role("link", name="Custom Clearance", exact=True)
        link.wait_for(state="visible")
        link.click()
        self.page.locator("h1.text:has-text('Ensure Fast and Compliant Shipments')").wait_for(state="visible")
        print("✅ Navigation to Customs Clearance: PASS")


    # ============================================================
    # Navigation: Hover Car Services menu, click Pre Export Inspection
    # ============================================================

    def go_to_pre_export_inspection(self):
        self.page.locator("p.cnm-cls", has_text="Car Services").hover()
        link = self.page.get_by_role("link", name="Pre Export Inspection", exact=True)
        link.wait_for(state="visible")
        link.click()
        self.page.locator("h2.title:has-text('Seal The Deal With Pre-Export Inspection')").wait_for(state="visible")
        print("✅ Navigation to Pre Export Inspection: PASS")


    # ============================================================
    # Navigation: Hover Car Services menu, click Marine Insurance Service
    # ============================================================

    def go_to_marine_insurance(self):
        self.page.locator("p.cnm-cls", has_text="Car Services").hover()
        link = self.page.get_by_role("link", name="Marine Insurance Service", exact=True)
        link.wait_for(state="visible")
        link.click()
        self.page.locator("img.banner-marine-insurance").wait_for(state="visible")
        print("✅ Navigation to Marine Insurance Service: PASS")


    # ============================================================
    # Navigation: Hover Car Services menu, click Non Stolen Vehicle Check
    # ============================================================

    def go_to_non_stolen_vehicle(self):
        self.page.locator("p.cnm-cls", has_text="Car Services").hover()
        link = self.page.get_by_role("link", name="Non Stolen Vehicle Check", exact=True)
        link.wait_for(state="visible")
        link.click()
        self.page.wait_for_url("**/non-stolen-vehicle", wait_until="domcontentloaded")
        print("✅ Navigation to Non Stolen Vehicle: PASS")
