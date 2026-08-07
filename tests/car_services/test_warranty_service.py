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

    assert warranty.get_main_heading() == "SAT Japan Warranty"
    assert (
        warranty.get_coverage_heading()
        == "What Does the SAT Japan Warranty Cover?"
    )
    assert warranty.get_claim_process_headings() == [
        "How to Report an Issue",
        "Step 1: Contact Us Within 48 Hours",
        "Step 2: We Assess Your Claim",
        "Step 3: Repair Begins",
        "Step 4: You Get Reimbursed",
    ]
    assert warranty.get_faq_heading() == "Frequently Asked Questions"

    print("\n✅ WARRANTY SERVICE COMPLETE")
