# ============================================================
# tests/car_services/test_storage_service.py
#
# HOW TO RUN:
#   pytest tests/car_services/test_storage_service.py -v -s
# ============================================================

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from pages.car_services.car_services_page import CarServicesPage
from pages.car_services.storage_service_page import StorageServicePage


def setup_storage_page(page):
    CarServicesPage(page).go_to_storage_service()
    return StorageServicePage(page)


# ============================================================
# Test 1: Verify Storage Service page loads with main heading
# ============================================================

def test_storage_page_loads(page):
    print("\n" + "="*60)
    print("🚢 TEST 1: STORAGE SERVICE PAGE LOAD")
    print("="*60)
    
    storage = setup_storage_page(page)
    storage.verify_main_heading()


# ============================================================
# Test 2: Verify Countries section heading
# ============================================================

def test_countries_section(page):
    print("\n" + "="*60)
    print("🌍 TEST 2: COUNTRIES SECTION")
    print("="*60)
    
    storage = setup_storage_page(page)
    storage.verify_countries_heading()


# ============================================================
# Test 3: Verify Benefits section heading
# ============================================================

def test_benefits_section(page):
    print("\n" + "="*60)
    print("⭐ TEST 3: BENEFITS SECTION")
    print("="*60)
    
    storage = setup_storage_page(page)
    storage.verify_benefits_heading()


# ============================================================
# Test 4: Verify Why Store section heading
# ============================================================

def test_why_store_section(page):
    print("\n" + "="*60)
    print("❓ TEST 4: WHY STORE SECTION")
    print("="*60)
    
    storage = setup_storage_page(page)
    storage.verify_why_store_heading()