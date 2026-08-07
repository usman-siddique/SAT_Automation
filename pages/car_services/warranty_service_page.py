class WarrantyServicePage:
    def __init__(self, page):
        self.page = page

    def verify_main_heading(self):
        heading = self.page.get_by_role("heading", name="SAT Japan Warranty", exact=True)
        heading.wait_for(state="visible")
        assert heading.inner_text().strip() == "SAT Japan Warranty"
        print("✅ Main heading verified: SAT Japan Warranty")

    def verify_coverage_section(self):
        heading_text = "What Does the SAT Japan Warranty Cover?"
        heading = self.page.get_by_role("heading", name=heading_text, exact=True)
        heading.wait_for(state="visible")
        assert heading.inner_text().strip() == heading_text
        print(f"✅ Coverage section verified: {heading_text}")

    def verify_claim_process(self):
        expected_headings = [
            "How to Report an Issue",
            "Step 1: Contact Us Within 48 Hours",
            "Step 2: We Assess Your Claim",
            "Step 3: Repair Begins",
            "Step 4: You Get Reimbursed",
        ]

        for heading_text in expected_headings:
            heading = self.page.get_by_role("heading", name=heading_text, exact=True)
            heading.wait_for(state="visible")
            assert heading.inner_text().strip() == heading_text
            print(f"✅ Claim process heading verified: {heading_text}")

    def verify_faq_section(self):
        heading = self.page.get_by_role(
            "heading", name="Frequently Asked Questions", exact=True
        )
        heading.wait_for(state="visible")
        assert heading.inner_text().strip() == "Frequently Asked Questions"
        print("✅ FAQ section verified: Frequently Asked Questions")
