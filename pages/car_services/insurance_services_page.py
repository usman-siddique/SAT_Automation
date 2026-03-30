# ============================================================
# pages/car_services/insurance_services_page.py
# Contains the InsuranceServicesPage class.
# Handles Insurance Services page content verification.
# ============================================================

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class InsuranceServicesPage:
    def __init__(self, page):
        self.page = page


    # ============================================================
    # Verify: Main heading is visible
    # ============================================================

    def verify_main_heading(self):
        self.page.locator("h1.insurance-bannar-title").wait_for(state="visible")
        heading_text = self.page.locator("h1.insurance-bannar-title").inner_text()
        assert "Comprehensive Car Insurance" in heading_text
        print(f"✅ Main heading verified: {heading_text}")


    # ============================================================
    # Verify: Coverage section heading is visible
    # ============================================================

    def verify_coverage_section(self):
        self.page.locator("h2:has-text('What Does Our Car Insurance Cover?')").wait_for(state="visible")
        coverage_text = self.page.locator("h2:has-text('What Does Our Car Insurance Cover?')").inner_text()
        assert "What Does Our Car Insurance Cover?" in coverage_text
        print(f"✅ Coverage section verified: {coverage_text}")


    # ============================================================
    # Verify: All 3 process subheadings are visible
    # ============================================================

    def verify_process_subheadings(self):
        # Page already loaded via navigation
        # Check immediately - don't wait
        
        if not self.page.locator("h3:has-text('Report the Issue')").is_visible():
            raise AssertionError("'Report the Issue' subheading not visible")
        print("✅ 'Report the Issue' subheading verified")
        
        if not self.page.locator("h3:has-text('Damage Claims Approval')").is_visible():
            raise AssertionError("'Damage Claims Approval' subheading not visible")
        print("✅ 'Damage Claims Approval' subheading verified")
        
        if not self.page.locator("h3:has-text('Damages Reimbursement')").is_visible():
            raise AssertionError("'Damages Reimbursement' subheading not visible")
        print("✅ 'Damages Reimbursement' subheading verified")

    # ============================================================
    # Verify: FAQ section heading is visible
    # ============================================================

    def verify_faq_section(self):
        self.page.locator("h2:has-text('Frequently Asked Questions')").wait_for(state="visible")
        faq_text = self.page.locator("h2:has-text('Frequently Asked Questions')").inner_text()
        assert "Frequently Asked Questions" in faq_text
        print(f"✅ FAQ section verified: {faq_text}")