# ============================================================
# tests/car_services/test_non_stolen_vehicle.py
#
# HOW TO RUN:
#   pytest tests/car_services/test_non_stolen_vehicle.py -v -s
# ============================================================

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import pytest
from pages.car_services.car_services_page import CarServicesPage
from pages.car_services.non_stolen_vehicle_page import NonStolenVehiclePage
from config import NON_STOLEN_VEHICLE_DATA


def setup_non_stolen_page(page_no_login):
    CarServicesPage(page_no_login).go_to_non_stolen_vehicle()
    return NonStolenVehiclePage(page_no_login)


# ============================================================
# Helper to open modal
# ============================================================

def open_modal(page_no_login):
    non_stolen = setup_non_stolen_page(page_no_login)
    non_stolen.verify_page_heading()
    non_stolen.open_modal()
    return non_stolen


# ============================================================
# Positive Test: Verify Non Stolen Vehicle form submission
# ============================================================

def test_non_stolen_vehicle_positive(require_state_changing_tests, page_no_login):
    print("\n" + "="*60)
    print("✅ NON STOLEN VEHICLE - POSITIVE TEST")
    print("="*60)
    
    non_stolen = open_modal(page_no_login)
    
    # Enter valid Stock ID from config
    non_stolen.enter_stock_id(NON_STOLEN_VEHICLE_DATA["valid_stock_id"])
    non_stolen.verify_car_details_loaded()
    
    # Fill all details correctly from config
    non_stolen.fill_personal_info(
        full_name=NON_STOLEN_VEHICLE_DATA["full_name"],
        email=NON_STOLEN_VEHICLE_DATA["email"],
        phone=NON_STOLEN_VEHICLE_DATA["phone"],
        select_country=True
    ).fill_payment_details(
        card_number=NON_STOLEN_VEHICLE_DATA["card_number_valid"],
        expiry=NON_STOLEN_VEHICLE_DATA["expiry"],
        cvc=NON_STOLEN_VEHICLE_DATA["cvc"],
        zip_code=NON_STOLEN_VEHICLE_DATA["zip_code"]
    ).submit_form()
    
    # Verify modal closes on success
    assert non_stolen.is_submission_successful(), "Page should refresh to non-stolen-vehicle and modal should be gone"
    
    print("\n✅ NON STOLEN VEHICLE POSITIVE TEST COMPLETE")


# ============================================================
# Negative Test 1: Invalid Stock ID
# ============================================================

def test_non_stolen_vehicle_invalid_stock_id(page_no_login):
    print("\n" + "="*60)
    print("❎ NON STOLEN VEHICLE - NEGATIVE: INVALID STOCK ID")
    print("="*60)
    
    non_stolen = open_modal(page_no_login)
    
    # Enter invalid Stock ID from config
    non_stolen.enter_stock_id(NON_STOLEN_VEHICLE_DATA["invalid_stock_id"])
    
    # Verify error message appears
    error = non_stolen.get_stock_id_error()
    assert error == "Stock ID not found.", f"Expected 'Stock ID not found.', got '{error}'"
    print(f"❎ Stock ID error verified: {error}")
    
    non_stolen.close_modal()
    print("\n✅ NEGATIVE TEST: INVALID STOCK ID COMPLETE")


# ============================================================
# Negative Test 2: Phone without country code
# ============================================================

def test_non_stolen_vehicle_no_country_code(require_state_changing_tests, page_no_login):
    print("\n" + "="*60)
    print("❎ NON STOLEN VEHICLE - NEGATIVE: NO COUNTRY CODE")
    print("="*60)
    
    non_stolen = open_modal(page_no_login)
    
    # Enter valid Stock ID from config
    non_stolen.enter_stock_id(NON_STOLEN_VEHICLE_DATA["valid_stock_id"])
    
    # Fill personal info without selecting country code
    non_stolen.fill_personal_info(
        full_name=NON_STOLEN_VEHICLE_DATA["full_name"],
        email=NON_STOLEN_VEHICLE_DATA["email"],
        phone=NON_STOLEN_VEHICLE_DATA["phone"],
        select_country=False  # Skip country code selection
    )
    
    # Try to submit
    non_stolen.submit_form()
    
    # Verify phone error message
    error = non_stolen.get_phone_error()
    assert error == "Please select country code", f"Expected 'Please select country code', got '{error}'"
    print(f"❎ Phone error verified: {error}")
    
    non_stolen.close_modal()
    print("\n✅ NEGATIVE TEST: NO COUNTRY CODE COMPLETE")


# ============================================================
# Negative Test 3: Incomplete card number
# ============================================================

def test_non_stolen_vehicle_incomplete_card(require_state_changing_tests, page_no_login):
    print("\n" + "="*60)
    print("❎ NON STOLEN VEHICLE - NEGATIVE: INCOMPLETE CARD")
    print("="*60)
    
    non_stolen = open_modal(page_no_login)
    
    # Enter valid Stock ID from config
    non_stolen.enter_stock_id(NON_STOLEN_VEHICLE_DATA["valid_stock_id"])
    
    # Fill personal info correctly
    non_stolen.fill_personal_info(
        full_name=NON_STOLEN_VEHICLE_DATA["full_name"],
        email=NON_STOLEN_VEHICLE_DATA["email"],
        phone=NON_STOLEN_VEHICLE_DATA["phone"],
        select_country=True
    )
    
    # Fill incomplete card (only 12 digits)
    non_stolen.fill_payment_details(
        card_number=NON_STOLEN_VEHICLE_DATA["card_number_incomplete"],
        expiry=NON_STOLEN_VEHICLE_DATA["expiry"],
        cvc=NON_STOLEN_VEHICLE_DATA["cvc"]
    )
    
    # Try to submit
    non_stolen.submit_form()
    
    # Verify payment error message
    error = non_stolen.get_payment_error()
    assert error == "Your card number is incomplete.", f"Expected 'Your card number is incomplete.', got '{error}'"
    print(f"❎ Payment error verified: {error}")
    
    non_stolen.close_modal()
    print("\n✅ NEGATIVE TEST: INCOMPLETE CARD COMPLETE")


# ============================================================
# Negative Test 4: Missing ZIP code
# ============================================================

def test_non_stolen_vehicle_missing_zip(require_state_changing_tests, page_no_login):
    print("\n" + "="*60)
    print("❎ NON STOLEN VEHICLE - NEGATIVE: MISSING ZIP CODE")
    print("="*60)
    
    non_stolen = open_modal(page_no_login)
    
    # Enter valid Stock ID from config
    non_stolen.enter_stock_id(NON_STOLEN_VEHICLE_DATA["valid_stock_id"])
    
    # Fill personal info correctly
    non_stolen.fill_personal_info(
        full_name=NON_STOLEN_VEHICLE_DATA["full_name"],
        email=NON_STOLEN_VEHICLE_DATA["email"],
        phone=NON_STOLEN_VEHICLE_DATA["phone"],
        select_country=True
    )
    
    # Fill card without ZIP
    non_stolen.fill_payment_details(
        card_number=NON_STOLEN_VEHICLE_DATA["card_number_valid"],
        expiry=NON_STOLEN_VEHICLE_DATA["expiry"],
        cvc=NON_STOLEN_VEHICLE_DATA["cvc"],
        zip_code=""  # Missing ZIP
    )
    
    # Try to submit
    non_stolen.submit_form()
    
    # Verify payment error message
    error = non_stolen.get_payment_error()
    assert error == "Your postal code is incomplete.", f"Expected 'Your postal code is incomplete.', got '{error}'"
    print(f"❎ Payment error verified: {error}")
    
    non_stolen.close_modal()
    print("\n✅ NEGATIVE TEST: MISSING ZIP CODE COMPLETE")
