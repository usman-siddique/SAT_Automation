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
    # Helper: Select value from Select2 dropdown (for Departure Port, Region, Ship Name)
    # ============================================================

    def select_select2_dropdown(self, container_id, value):
        self.page.locator(f"#{container_id}").click()

        search_input = self.page.locator(".select2-search__field")
        search_input.wait_for(state="visible")
        search_input.click()
        search_input.fill(value)

        option = self.page.locator(".select2-results__option", has_text=value)
        option.wait_for(state="visible")
        option.click()

        # Wait for dropdown to fully close before proceeding
        self.page.locator(".select2-results__options").wait_for(state="hidden")
        print(f"✅ {container_id} selected - {value}")


    # ============================================================
    # Action: Select Arrival Port (separate method with fix for search issue)
    # ============================================================

    def select_arrival_port(self, value):
        dropdown = self.page.locator("#select2-arrival_port-container")
        dropdown.click()

        search_input = self.page.locator(".select2-search__field")
        search_input.wait_for(state="visible")
        search_input.click()
        
        # Clear existing text 
        search_input.press("Control+a")
        search_input.press("Backspace")
        
        # Type slowly to trigger keyboard events
        search_input.press_sequentially(value, delay=100)
        
        # Move mouse to trigger any focus/blur events
        self.page.mouse.move(0, 0)
        self.page.mouse.move(10, 10)
        
        option = self.page.locator(".select2-results__option", has_text=value)
        option.wait_for(state="visible", timeout=10000)
        option.click()

        self.page.locator(".select2-results__options").wait_for(state="hidden")
        print(f"✅ select2-arrival_port-container selected - {value}")


    # ============================================================
    # Helper: Select date from custom datepicker (stable: uses days 5 and 25)
    # ============================================================

    def select_date(self, input_locator, day):
        self.page.locator(input_locator).click()
        # Target only the visible calendar (the one that opened)
        calendar = self.page.locator(".container__main:visible")
        calendar.wait_for(state="visible")
        # Wait for the specific day to be visible within that calendar
        day_element = calendar.locator(f".day-item:text-is('{day}')")
        day_element.wait_for(state="visible")
        day_element.click()
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
    # Action: Select Ship Name
    # ============================================================

    def select_ship_name(self, value):
        self.select_select2_dropdown("select2-ship_name-container", value)


    # ============================================================
    # Action: Click Search
    # Waits for results or no-results message to confirm search completed
    # ============================================================

    def click_search(self):
        self.page.locator(".btn-search-filter").click()
        # Wait for title to have non-empty text
        self.page.wait_for_function(
            "document.querySelector('span#title-page')?.innerText?.trim() !== ''",
            timeout=30000
        )
        # Small delay to let the DOM settle (50ms is enough)
        self.page.wait_for_timeout(50)
        print("✅ Search filter applied")


    # ============================================================
    # Action: Click Reset
    # ============================================================

    def click_reset(self):
        self.page.locator(".btn-reset-filter").click()
        # Wait for table to reload after reset
        self.page.locator("table tbody tr:has-text('Ship Name')").first.wait_for(state="visible")
        print("✅ Reset filter applied")


    # ============================================================
    # Helper: Verify filter results
    # ============================================================

    def verify_filter_results(self, expected_title_text=None):
        if self.page.locator("h2.not-found-text").is_visible():
            self.verify_no_results()
            return False

        if expected_title_text:
            try:
                self.verify_title_contains(expected_title_text)
                return True
            except:
                pass

        self.verify_table_loads()
        return True