class BankInformationPage:
    CURRENCY_SECTIONS = (
        "Bank Information (USD)",
        "Bank Information (EUR)",
        "Bank Information (JPY)",
        "Bank Information (AUD)",
        "Bank Information (GBP)",
        "Bank Information (NZD)",
        "Bank Information (CAD)",
        "Bank Information (CNY)",
    )

    def __init__(self, page):
        self.page = page

    def get_currency_sections(self):
        sections = []
        for name in self.CURRENCY_SECTIONS:
            heading = self.page.get_by_role("heading", name=name, exact=True)
            heading.wait_for(state="visible")
            sections.append(heading.inner_text().strip())
        return sections

    def get_detail_labels(self):
        labels = ("Bank Name:", "Swift Code:", "Branch Name:", "Account Number:")
        visible = []
        for label in labels:
            item = self.page.get_by_role("heading", name=label, exact=True).first
            item.wait_for(state="visible")
            visible.append(item.inner_text().strip())
        return visible
