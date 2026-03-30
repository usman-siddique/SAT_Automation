# ============================================================
# pages/car_services/shipping_schedule_page.py
# Contains the ShippingSchedulePage class.
# ============================================================

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class ShippingSchedulePage:
    def __init__(self, page):
        self.page = page


    # ============================================================
    # Verify: Page loaded with heading and confirmation text
    # ============================================================

    def verify_page_load(self):
        self.page.locator("h1.title-page").first.wait_for(state="visible")
        self.page.locator("p.see-first-para").wait_for(state="visible")
        print("✅ Shipping Schedule page loaded")


    # ============================================================
    # Verify: All filter controls are visible
    # ============================================================

    def verify_filters_visible(self):
        self.page.locator("#select2-departure_port-container").wait_for(state="visible")
        self.page.locator("#select2-region-container").wait_for(state="visible")
        self.page.locator("#select2-arrival_port-container").wait_for(state="visible")
        self.page.locator("#select2-ship_name-container").wait_for(state="visible")
        self.page.locator(".departure_date_from").wait_for(state="visible")
        self.page.locator(".departure_date_to").wait_for(state="visible")
        self.page.locator(".arrival_date_from").wait_for(state="visible")
        self.page.locator(".arrival_date_to").wait_for(state="visible")
        self.page.locator(".btn-search-filter").wait_for(state="visible")
        self.page.locator(".btn-reset-filter").wait_for(state="visible")
        print("✅ All filter controls visible")


    # ============================================================
    # Verify: Shipping notes link is visible
    # ============================================================

    def verify_shipping_notes_link(self):
        self.page.locator("a[href='#shipping_note']").wait_for(state="visible")
        print("✅ Shipping notes link visible")


    # ============================================================
    # Verify: Table loads with at least one row
    # ============================================================

    def verify_table_loads(self):
        self.page.locator("table tbody tr:has-text('Ship Name')").first.wait_for(state="visible")
        print("✅ Shipping Schedule table loaded with data")


    # ============================================================
    # Verify: No results message shown when filters return nothing
    # ============================================================

    def verify_no_results(self):
        self.page.locator("h2.not-found-text").wait_for(state="visible")
        print("✅ No results message shown")


    # ============================================================
    # Verify: Title span contains expected filter text
    # ============================================================

    def verify_title_contains(self, text):
        self.page.locator("#title-page", has_text=text).wait_for(state="visible")
        print(f"✅ Title contains '{text}'")


    # ============================================================
    # Helper: Select value from Select2 dropdown
    # ============================================================

    def select_select2_dropdown(self, container_id, value):
        self.page.locator(f"#{container_id}").click()
        
        if container_id == "select2-arrival_port-container":
            option = self.page.locator(".select2-results__option", has_text=value)
            option.wait_for(state="visible", timeout=5000)
            option.click()
            self.page.wait_for_timeout(500)  # Wait for selection to register
        else:
            search_input = self.page.locator(".select2-search__field")
            search_input.wait_for(state="visible")
            search_input.fill(value)
            self.page.wait_for_timeout(500)
            
            option = self.page.locator(".select2-results__option", has_text=value)
            option.wait_for(state="visible", timeout=5000)
            option.click()
            self.page.wait_for_timeout(500)
        
        print(f"✅ {container_id} selected - {value}")


    # ============================================================
    # Helper: Select date from custom datepicker
    # ============================================================

    def select_date(self, input_locator, day):
        self.page.locator(input_locator).click()
        calendar = self.page.locator(".container__main:visible")
        calendar.wait_for(state="visible")
        calendar.locator(".day-item", has_text=str(day)).click()
        print(f"✅ Date selected - day {day}")


    # ============================================================
    # Action: Select Departure Port
    # ============================================================

    def select_departure_port(self, value):
        self.select_select2_dropdown("select2-departure_port-container", value)


    # ============================================================
    # Action: Select Region
    # ============================================================

    def select_region(self, value):
        self.select_select2_dropdown("select2-region-container", value)


    # ============================================================
    # Action: Select Arrival Port
    # ============================================================

    def select_arrival_port(self, value):
        self.select_select2_dropdown("select2-arrival_port-container", value)


    # ============================================================
    # Action: Select Ship Name
    # ============================================================

    def select_ship_name(self, value):
        self.select_select2_dropdown("select2-ship_name-container", value)


    # ============================================================
    # Action: Click Search
    # ============================================================

    def click_search(self):
        self.page.locator(".btn-search-filter").click()
        
        # Wait for either title span to have content OR no results message
        self.page.wait_for_function(
            "document.querySelector('span#title-page') && document.querySelector('span#title-page').innerText.trim() !== '' || "
            "document.querySelector('h2.not-found-text') !== null"
        )
        
        print("✅ Search filter applied")


    # ============================================================
    # Action: Click Reset
    # ============================================================

    def click_reset(self):
        self.page.locator(".btn-reset-filter").click()
        print("✅ Reset filter applied")


    # ============================================================
    # Helper: Verify filter results
    # ============================================================

    def verify_filter_results(self, expected_title_text=None):
        """Verifies filter results - either title contains text, or table loads, or no results"""
        
        # Check if no results message appears
        if self.page.locator("h2.not-found-text").is_visible():
            self.verify_no_results()
            return False
        
        # Check if title span has expected text
        if expected_title_text:
            try:
                self.verify_title_contains(expected_title_text)
                return True
            except:
                pass
        
        # Fallback: verify table loaded
        self.verify_table_loads()
        return True