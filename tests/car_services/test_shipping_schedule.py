# ============================================================
# tests/car_services/test_shipping_schedule.py
#
# HOW TO RUN:
#   pytest tests/car_services/test_shipping_schedule.py -v -s
# ============================================================

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from pages.car_services.car_services_page import CarServicesPage
from pages.car_services.shipping_schedule_page import ShippingSchedulePage


def setup_shipping_schedule(page):
    CarServicesPage(page).go_to_shipping_schedule()
    return ShippingSchedulePage(page)


# ============================================================
# Test 1: Verify page loads and basic elements
# ============================================================

def test_page_verification(page):
    print("\n" + "="*60)
    print("🚢 TEST 1: PAGE VERIFICATION")
    print("="*60)
    
    shipping = setup_shipping_schedule(page)
    
    shipping.verify_page_load()
    shipping.verify_filters_visible()
    shipping.verify_table_loads()
    shipping.verify_shipping_notes_link()
    
    print("\n✅ PAGE VERIFICATION COMPLETE")


# ============================================================
# Test 2: All dropdown filters combined
# ============================================================

def test_all_dropdown_filters(page):
    print("\n" + "="*60)
    print("📝 TEST 2: ALL DROPDOWN FILTERS COMBINED")
    print("="*60)
    
    shipping = setup_shipping_schedule(page)
    
    # Apply all 4 dropdown filters
    print("\nApplying: Yokohama + Africa + Durban + Orion Leader")
    shipping.select_departure_port("Yokohama")
    shipping.select_region("Africa")
    shipping.select_arrival_port("Durban")
    shipping.select_ship_name("Orion Leader")
    shipping.click_search()
    
    # Verify results - should show title with filter values
    title_text = shipping.page.locator("span#title-page").inner_text().strip()
    if title_text:
        assert "Orion Leader" in title_text or "Yokohama" in title_text or "Durban" in title_text
        print(f"✅ Verified - title shows: {title_text}")
    else:
        # If no title, check if no results message appears
        shipping.verify_no_results()
    
    shipping.click_reset()
    print("\n✅ DROPDOWN FILTERS TEST COMPLETE")


# ============================================================
# Test 3: All date filters combined
# ============================================================

def test_all_date_filters(page):
    print("\n" + "="*60)
    print("📅 TEST 3: ALL DATE FILTERS COMBINED")
    print("="*60)
    
    shipping = setup_shipping_schedule(page)
    
    # Apply both date ranges
    print("\nApplying: Departure Date 15-30 + Arrival Date 15-30")
    shipping.select_date(".departure_date_from", 15)
    shipping.select_date(".departure_date_to", 30)
    shipping.select_date(".arrival_date_from", 15)
    shipping.select_date(".arrival_date_to", 30)
    shipping.click_search()
    
    # Verify results
    shipping.verify_filter_results()
    
    shipping.click_reset()
    print("\n✅ DATE FILTERS TEST COMPLETE")