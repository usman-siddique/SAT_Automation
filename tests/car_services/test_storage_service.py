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


def setup_storage_page(page_no_login):
    CarServicesPage(page_no_login).go_to_storage_service()
    return StorageServicePage(page_no_login)


# ============================================================
# Test: Verify all Storage Service page elements
# ============================================================

def test_storage_service_all(page_no_login):
    print("\n" + "="*60)
    print("✅ STORAGE SERVICE - COMPLETE VERIFICATION")
    print("="*60)
    
    storage = setup_storage_page(page_no_login)

    assert (
        storage.get_main_heading()
        == "Secure Storage Service For Your Vehicle's Safety"
    )
    assert (
        storage.get_countries_heading()
        == "Countries Where We Offer Storage Service"
    )
    assert (
        storage.get_benefits_heading()
        == "Benefits of SAT Vehicle Storage Service"
    )
    assert storage.get_why_store_heading() == "Why Store a New Vehicle?"
    
    print("\n✅ STORAGE SERVICE COMPLETE")
