class SafeBuyingGuidePage:
    def __init__(self, page):
        self.page = page

    def get_safety_sections(self):
        names = (
            "How to Beware Of Fraudulent Activities",
            "Cyber Safety Precaution",
            "Staying Safe the SAT Way",
            "What Our Vehicle Checks Offer",
        )
        sections = []
        for name in names:
            section = self.page.get_by_text(name, exact=True)
            section.wait_for(state="visible")
            sections.append(section.inner_text().strip())
        return sections
