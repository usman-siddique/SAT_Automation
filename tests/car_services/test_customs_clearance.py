# ============================================================
# tests/car_services/test_customs_clearance.py
#
# HOW TO RUN:
#   pytest tests/car_services/test_customs_clearance.py -v -s
# ============================================================

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from pages.car_services.car_services_page import CarServicesPage
from pages.car_services.customs_clearance_page import CustomsClearancePage


def setup_customs_clearance_page(page_no_login):
    CarServicesPage(page_no_login).go_to_customs_clearance()
    return CustomsClearancePage(page_no_login)


# ============================================================
# Test: Verify all Customs Clearance page elements
# ============================================================

def test_customs_clearance_all(page_no_login):
    print("\n" + "="*60)
    print("✅ CUSTOMS CLEARANCE - COMPLETE VERIFICATION")
    print("="*60)
    
    customs = setup_customs_clearance_page(page_no_login)
    
    # Verify all elements on single page
    customs.verify_main_heading()
    customs.verify_image()
    customs.verify_steps_heading()
    
    print("\n✅ CUSTOMS CLEARANCE COMPLETE")