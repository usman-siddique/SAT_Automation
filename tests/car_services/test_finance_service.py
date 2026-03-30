# ============================================================
# tests/car_services/test_finance_service.py
#
# HOW TO RUN:
#   pytest tests/car_services/test_finance_service.py -v -s
# ============================================================

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from pages.car_services.car_services_page import CarServicesPage
from pages.car_services.finance_service_page import FinanceServicePage


def setup_finance_page(page):
    CarServicesPage(page).go_to_finance_service()
    return FinanceServicePage(page)


# ============================================================
# Test 1: Verify all Finance Service page elements
# ============================================================

def test_finance_service_all(page):
    print("\n" + "="*60)
    print("💰 FINANCE SERVICE - COMPLETE VERIFICATION")
    print("="*60)
    
    finance = setup_finance_page(page)
    
    # Verify banner
    finance.verify_banner_image()
    
    # Verify main heading
    finance.verify_main_heading()
    
    # Verify and play video
    finance.verify_and_play_video()
    
    print("\n✅ FINANCE SERVICE COMPLETE")