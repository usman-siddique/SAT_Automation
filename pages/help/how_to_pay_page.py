class HowToPayPage:
    def __init__(self, page):
        self.page = page

    def get_main_heading(self):
        heading = self.page.get_by_role("heading", name="How to Pay", exact=True)
        heading.wait_for(state="visible")
        return heading.inner_text().strip()

    def get_payment_method_headings(self):
        names = (
            "Bank Transfer",
            "Credit/Debit Card",
            "PayPal",
            "Visit Our Nearest Branch",
        )
        headings = []
        for name in names:
            heading = self.page.get_by_role("heading", name=name, exact=True)
            heading.wait_for(state="visible")
            headings.append(heading.inner_text().strip())
        return headings
