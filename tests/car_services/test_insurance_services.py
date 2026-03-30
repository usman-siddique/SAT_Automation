# ============================================================
# tests/car_services/test_insurance_services.py
#
# HOW TO RUN:
#   pytest tests/car_services/test_insurance_services.py -v -s
# ============================================================

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from pages.car_services.car_services_page import CarServicesPage
from pages.car_services.insurance_services_page import InsuranceServicesPage


def setup_insurance_page(page):
    CarServicesPage(page).go_to_insurance_services()
    return InsuranceServicesPage(page)


# ============================================================
# Test 1: Verify Insurance Services page loads with main heading
# ============================================================

def test_insurance_page_loads(page):
    print("\n" + "="*60)
    print("🚢 TEST 1: INSURANCE SERVICES PAGE LOAD")
    print("="*60)
    
    insurance = setup_insurance_page(page)
    insurance.verify_main_heading()


# ============================================================
# Test 2: Verify Coverage section heading
# ============================================================

def test_coverage_section(page):
    print("\n" + "="*60)
    print("📋 TEST 2: COVERAGE SECTION")
    print("="*60)
    
    insurance = setup_insurance_page(page)
    insurance.verify_coverage_section()


# ============================================================
# Test 3: Verify all 3 process subheadings
# ============================================================

def test_process_subheadings(page):
    print("\n" + "="*60)
    print("📝 TEST 3: PROCESS SUBHEADINGS")
    print("="*60)
    
    insurance = setup_insurance_page(page)
    insurance.verify_process_subheadings()


# ============================================================
# Test 4: Verify FAQ section exists
# ============================================================

def test_faq_section(page):
    print("\n" + "="*60)
    print("📝 TEST 4: FAQ SECTION")
    print("="*60)
    
    insurance = setup_insurance_page(page)
    insurance.verify_faq_section()