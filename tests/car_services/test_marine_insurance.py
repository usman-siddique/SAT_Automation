# ============================================================
# tests/car_services/test_marine_insurance.py
#
# HOW TO RUN:
#   pytest tests/car_services/test_marine_insurance.py -v -s
# ============================================================

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from pages.car_services.car_services_page import CarServicesPage
from pages.car_services.marine_insurance_page import MarineInsurancePage


def setup_marine_insurance_page(page_no_login):
    CarServicesPage(page_no_login).go_to_marine_insurance()
    return MarineInsurancePage(page_no_login)


# ============================================================
# Test: Verify all Marine Insurance Service page elements
# ============================================================

def test_marine_insurance_all(page_no_login):
    print("\n" + "="*60)
    print("✅ MARINE INSURANCE SERVICE - COMPLETE VERIFICATION")
    print("="*60)
    
    marine = setup_marine_insurance_page(page_no_login)
    
    # Verify all elements on single page
    marine.verify_banner_image()
    marine.verify_coverage_heading()
    marine.verify_steps_heading()
    
    print("\n✅ MARINE INSURANCE SERVICE COMPLETE")