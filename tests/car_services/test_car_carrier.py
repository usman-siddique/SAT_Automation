# ============================================================
# tests/car_services/test_car_carrier.py
#
# HOW TO RUN:
#   pytest tests/car_services/test_car_carrier.py -v -s
# ============================================================

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from pages.car_services.car_services_page import CarServicesPage
from pages.car_services.car_carrier_page import CarCarrierPage


def setup_car_carrier_page(page_no_login):
    CarServicesPage(page_no_login).go_to_car_carrier_service()
    return CarCarrierPage(page_no_login)


# ============================================================
# Test: Verify all Car Carrier Service page elements
# ============================================================

def test_car_carrier_service_all(page_no_login):
    print("\n" + "="*60)
    print("✅ CAR CARRIER SERVICE - COMPLETE VERIFICATION")
    print("="*60)
    
    carrier = setup_car_carrier_page(page_no_login)
    
    # Verify all elements on single page
    carrier.verify_delivery_options_heading()
    carrier.verify_benefits_heading()
    carrier.verify_images()
    
    print("\n✅ CAR CARRIER SERVICE COMPLETE")