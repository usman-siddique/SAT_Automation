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


def setup_insurance_page(page_no_login):
    CarServicesPage(page_no_login).go_to_insurance_services()
    return InsuranceServicesPage(page_no_login)


# ============================================================
# Test: Verify all Insurance Services page elements
# ============================================================

def test_insurance_services_all(page_no_login):
    print("\n" + "="*60)
    print("✅ INSURANCE SERVICES - COMPLETE VERIFICATION")
    print("="*60)
    
    insurance = setup_insurance_page(page_no_login)
    
    # Verify all elements on single page
    insurance.verify_main_heading()
    insurance.verify_coverage_section()
    insurance.verify_process_subheadings()
    insurance.verify_faq_section()
    
    print("\n✅ INSURANCE SERVICES COMPLETE")