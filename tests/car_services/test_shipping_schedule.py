# ============================================================
# tests/car_services/test_shipping_schedule.py
#
# HOW TO RUN:
#   pytest tests/car_services/test_shipping_schedule.py -v -s
# ============================================================

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import pytest
from pages.car_services.car_services_page import CarServicesPage
from pages.car_services.shipping_schedule_page import ShippingSchedulePage
from config import SHIPPING_SCHEDULE_SCENARIOS


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
# Test 2: All dropdown filters combined (Parameterized)
# ============================================================

@pytest.mark.parametrize("scenario", SHIPPING_SCHEDULE_SCENARIOS)
def test_all_dropdown_filters(page, scenario):
    print("\n" + "="*60)
    print(f"📝 TEST 2: ALL DROPDOWN FILTERS COMBINED - {scenario['name']}")
    print("="*60)
    
    shipping = setup_shipping_schedule(page)
    
    # Apply all 4 dropdown filters from scenario
    print(f"\nApplying: {scenario['departure_port']} + "
          f"{scenario['region']} + "
          f"{scenario['arrival_port']} + "
          f"{scenario['ship_name']}")
    
    shipping.select_departure_port(scenario["departure_port"])
    shipping.select_region(scenario["region"])
    shipping.select_arrival_port(scenario["arrival_port"])
    shipping.select_ship_name(scenario["ship_name"])
    shipping.click_search()
    
    # Check based on expected outcome
    if scenario["expected"] == "no_results":
        # Verify no results message appears
        shipping.verify_no_results()
        print("✅ No results found - test passed (filters returned empty)")
    else:
        # Verify results found
        title_text = shipping.page.locator("span#title-page").inner_text().strip()
        assert title_text, "❌ Title should have content when results found"
        print(f"✅ Verified - title shows: {title_text}")
    
    shipping.click_reset()
    print("\n✅ DROPDOWN FILTERS TEST COMPLETE")


# ============================================================
# Test 3: All date filters combined (Parameterized)
# ============================================================

@pytest.mark.parametrize("scenario", SHIPPING_SCHEDULE_SCENARIOS)
def test_all_date_filters(page, scenario):
    print("\n" + "="*60)
    print(f"📅 TEST 3: ALL DATE FILTERS COMBINED - {scenario['name']}")
    print("="*60)
    
    shipping = setup_shipping_schedule(page)
    
    # Apply both date ranges from config
    print("\nApplying: Departure Date 15-30 + Arrival Date 15-30")
    shipping.select_date(".departure_date_from", 15)
    shipping.select_date(".departure_date_to", 30)
    shipping.select_date(".arrival_date_from", 15)
    shipping.select_date(".arrival_date_to", 30)
    shipping.click_search()
    
    # Check based on expected outcome
    if scenario["expected"] == "no_results":
        shipping.verify_no_results()
        print("✅ No results found - test passed (filters returned empty)")
    else:
        shipping.verify_filter_results()
    
    shipping.click_reset()
    print("\n✅ DATE FILTERS TEST COMPLETE")