from pages.car_services.car_services_page import CarServicesPage
from pages.car_services.warranty_service_page import WarrantyServicePage


def setup_warranty_page(page_no_login):
    CarServicesPage(page_no_login).go_to_warranty_service()
    return WarrantyServicePage(page_no_login)


def test_warranty_service_all(page_no_login):
    print("\n" + "=" * 60)
    print("✅ WARRANTY SERVICE - COMPLETE VERIFICATION")
    print("=" * 60)

    warranty = setup_warranty_page(page_no_login)
    warranty.verify_main_heading()
    warranty.verify_coverage_section()
    warranty.verify_claim_process()
    warranty.verify_faq_section()

    print("\n✅ WARRANTY SERVICE COMPLETE")
