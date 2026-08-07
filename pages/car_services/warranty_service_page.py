class WarrantyServicePage:
    def __init__(self, page):
        self.page = page

    def get_main_heading(self):
        heading = self.page.get_by_role("heading", name="SAT Japan Warranty", exact=True)
        heading.wait_for(state="visible")
        return heading.inner_text().strip()

    def get_coverage_heading(self):
        heading_text = "What Does the SAT Japan Warranty Cover?"
        heading = self.page.get_by_role("heading", name=heading_text, exact=True)
        heading.wait_for(state="visible")
        return heading.inner_text().strip()

    def get_claim_process_headings(self):
        heading_names = [
            "How to Report an Issue",
            "Step 1: Contact Us Within 48 Hours",
            "Step 2: We Assess Your Claim",
            "Step 3: Repair Begins",
            "Step 4: You Get Reimbursed",
        ]

        visible_headings = []
        for heading_name in heading_names:
            heading = self.page.get_by_role("heading", name=heading_name, exact=True)
            heading.wait_for(state="visible")
            visible_headings.append(heading.inner_text().strip())

        return visible_headings

    def get_faq_heading(self):
        heading = self.page.get_by_role(
            "heading", name="Frequently Asked Questions", exact=True
        )
        heading.wait_for(state="visible")
        return heading.inner_text().strip()
