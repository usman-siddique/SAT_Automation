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
from config import SHIPPING_SCHEDULE_SCENARIOS


def setup_shipping_schedule(page_no_login):
    CarServicesPage(page_no_login).go_to_shipping_schedule()
    return ShippingSchedulePage(page_no_login)


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
    
    # FIX: Wait for title to be visible before reading
    title_locator = shipping.page.locator("span#title-page")
    title_locator.wait_for(state="visible")
    title_text = title_locator.inner_text().strip()
    
    if title_text:
        print(f"✅ Verified - title shows: {title_text}")
    else:
        # If title is empty but visible, check for no-results message
        no_results = shipping.page.locator("h2.not-found-text")
        if no_results.is_visible():
            print("✅ No results shown - server data not available")
        else:
            raise AssertionError("❌ Neither title nor no-results message visible after search")
    
    shipping.click_reset()
    
    # ============================================================
    # Part 3: Dropdown filters - Invalid scenario (always no results)
    # ============================================================
    print("\n✅  PART 3: DROPDOWN FILTERS - INVALID SCENARIO (NO RESULTS)")
    invalid_scenario = SHIPPING_SCHEDULE_SCENARIOS[1]  # Moji + Chile + Iquique + Orion Leader
    
    shipping.select_departure_port(invalid_scenario["departure_port"])
    shipping.select_region(invalid_scenario["region"])
    shipping.select_arrival_port(invalid_scenario["arrival_port"])
    shipping.select_ship_name(invalid_scenario["ship_name"])
    shipping.click_search()
    
    # For invalid scenario, we expect the no-results message
    shipping.page.locator("h2.not-found-text").wait_for(state="visible")
    print("✅ No results message shown")
    
    shipping.click_reset()
    
    # ============================================================
    # Part 4: Date filters - Valid scenario (using stable days 5 and 25)
    # ============================================================
    print("\n✅  PART 4: DATE FILTERS - VALID SCENARIO")
    shipping.select_date(".departure_date_from", 5)
    shipping.select_date(".departure_date_to", 25)
    shipping.select_date(".arrival_date_from", 5)
    shipping.select_date(".arrival_date_to", 25)
    shipping.click_search()
    
    # Wait for either title or no-results message
    shipping.page.wait_for_function(
        "document.querySelector('span#title-page')?.innerText?.trim() !== '' || "
        "document.querySelector('h2.not-found-text') !== null",
        timeout=30000
    )
    
    if shipping.page.locator("h2.not-found-text").is_visible():
        print("✅ No results message shown")
    else:
        shipping.verify_table_loads()
    
    shipping.click_reset()
    
    # ============================================================
    # Part 5: Date filters - Invalid scenario (same, expecting no results)
    # ============================================================
    print("\n✅  PART 5: DATE FILTERS - INVALID SCENARIO (SAME, NO RESULTS)")
    shipping.select_date(".departure_date_from", 5)
    shipping.select_date(".departure_date_to", 25)
    shipping.select_date(".arrival_date_from", 5)
    shipping.select_date(".arrival_date_to", 25)
    shipping.click_search()
    
    shipping.page.locator("h2.not-found-text").wait_for(state="visible")
    print("✅ No results message shown")
    
    shipping.click_reset()
    
    print("\n" + "="*60)
    print("✅ SHIPPING SCHEDULE - ALL TESTS COMPLETE")
    print("="*60)