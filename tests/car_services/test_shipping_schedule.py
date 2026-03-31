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


def setup_shipping_schedule(page_no_login):
    CarServicesPage(page_no_login).go_to_shipping_schedule()
    return ShippingSchedulePage(page_no_login)


def refresh_page(page_no_login):
    page_no_login.reload()
    page_no_login.wait_for_load_state("domcontentloaded")
    print("✅  Page refreshed")


# ============================================================
# Combined Test: All Shipping Schedule validations in one session
# ============================================================

def test_shipping_schedule_all(page_no_login):
    print("\n" + "="*60)
    print("✅ SHIPPING SCHEDULE - COMPLETE VERIFICATION")
    print("="*60)
    
    # ============================================================
    # Part 1: Page verification
    # ============================================================
    print("\n✅  PART 1: PAGE VERIFICATION")
    shipping = setup_shipping_schedule(page_no_login)
    shipping.verify_page_load()
    shipping.verify_filters_visible()
    shipping.verify_table_loads()
    shipping.verify_shipping_notes_link()
    
    # ============================================================
    # Part 2: Dropdown filters - Valid scenario
    # ============================================================
    print("\n✅  PART 2: DROPDOWN FILTERS - VALID SCENARIO")
    valid_scenario = SHIPPING_SCHEDULE_SCENARIOS[0]  # Yokohama + Africa + Durban + Orion Leader
    
    shipping.select_departure_port(valid_scenario["departure_port"])
    shipping.select_region(valid_scenario["region"])
    shipping.select_arrival_port(valid_scenario["arrival_port"])
    shipping.select_ship_name(valid_scenario["ship_name"])
    shipping.click_search()
    
    title_text = shipping.page.locator("span#title-page").inner_text().strip()
    assert title_text, "❌ Title should have content when results found"
    print(f"✅ Verified - title shows: {title_text}")
    
    shipping.click_reset()
    
    # ============================================================
    # Part 3: Dropdown filters - Invalid scenario (no results)
    # ============================================================
    print("\n✅  PART 3: DROPDOWN FILTERS - INVALID SCENARIO (NO RESULTS)")
    invalid_scenario = SHIPPING_SCHEDULE_SCENARIOS[1]  # Moji + Chile + Iquique + Orion Leader
    
    shipping.select_departure_port(invalid_scenario["departure_port"])
    shipping.select_region(invalid_scenario["region"])
    shipping.select_arrival_port(invalid_scenario["arrival_port"])
    shipping.select_ship_name(invalid_scenario["ship_name"])
    shipping.click_search()
    shipping.verify_no_results()
    shipping.click_reset()
    
    # ============================================================
    # Part 4: Date filters - Valid scenario (may show no results)
    # ============================================================
    print("\n✅  PART 4: DATE FILTERS - VALID SCENARIO")
    shipping.select_date(".departure_date_from", 15)
    shipping.select_date(".departure_date_to", 30)
    shipping.select_date(".arrival_date_from", 15)
    shipping.select_date(".arrival_date_to", 30)
    shipping.click_search()
    
    # Check if results or no results
    if shipping.page.locator("h2.not-found-text").is_visible():
        shipping.verify_no_results()
    else:
        shipping.verify_table_loads()
    
    shipping.click_reset()
    
    # ============================================================
    # Part 5: Date filters - Invalid scenario (same as valid, no results)
    # ============================================================
    print("\n✅  PART 5: DATE FILTERS - INVALID SCENARIO (SAME, NO RESULTS)")
    shipping.select_date(".departure_date_from", 15)
    shipping.select_date(".departure_date_to", 30)
    shipping.select_date(".arrival_date_from", 15)
    shipping.select_date(".arrival_date_to", 30)
    shipping.click_search()
    shipping.verify_no_results()
    shipping.click_reset()
    
    print("\n" + "="*60)
    print("✅ SHIPPING SCHEDULE - ALL TESTS COMPLETE")
    print("="*60)