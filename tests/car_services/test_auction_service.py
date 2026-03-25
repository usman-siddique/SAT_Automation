# ============================================================
# tests/car_services/test_auction_service.py
#
# HOW TO RUN:
#   pytest SAT_Automation/tests/car_services/test_auction_service.py -v --html=SAT_Automation/reports/report.html
# ============================================================

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from pages.car_services.car_services_page import CarServicesPage


# ============================================================
# Test 1: Verify navigation to Auction Service page
# ============================================================

def test_navigate_to_auction_service(page):
    print("\n📝 Starting Auction Service Navigation...")
    car_services = CarServicesPage(page)
    car_services.go_to_auction_service()
