class UsedCarGuidePage:
    def __init__(self, page):
        self.page = page

    def get_guide_headings(self):
        names = (
            "Overview",
            "Choose a Used Car by Category",
            "Determine the Purpose of Purchase",
            "Make the Purchase Process Convenient with SAT",
        )
        headings = []
        for name in names:
            heading = self.page.get_by_role("heading", name=name, exact=True)
            heading.wait_for(state="visible")
            headings.append(heading.inner_text().strip())
        return headings
