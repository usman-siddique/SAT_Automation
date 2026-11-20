"""Page object for the SAT Japan Warranty service."""

from urllib.parse import urlparse

from pages.car_services.image_assertions import assert_image_loaded


class WarrantyServicePage:
    COVERAGE_ITEMS = [
        "Partial Damage",
        "Breakage / Dents",
        "Engine Issues",
        "Transmission Issues",
        "Electrical Issues",
        "Missing Items",
    ]

    CLAIM_HEADINGS = [
        "How to Report an Issue",
        "Step 1: Contact Us Within 48 Hours",
        "Step 2: We Assess Your Claim",
        "Step 3: Repair Begins",
        "Step 4: You Get Reimbursed",
    ]

    FAQ_QUESTIONS = [
        "What issues are covered under the SAT Japan Warranty?",
        "How long do I have to report a problem?",
        "Can I start repairs before getting approval?",
        "How long does the assessment take?",
        "Who decides the repair method and reimbursement amount?",
        (
            "What if my vehicle was damaged during shipping, but the issue "
            "is not mechanical?"
        ),
        "How do I contact SAT Japan about a warranty claim?",
    ]

    FAQ_ANSWER_KEYWORDS = [
        "Expendable Exemption List",
        "48 hours",
        "before we approve",
        "2 to 3 business days",
        "SAT Japan evaluates",
        "48-hour window",
        "info@satjapan.com",
    ]

    def __init__(self, page):
        self.page = page

    def verify_page_contract(self):
        main_heading = self.page.get_by_role(
            "heading", name="SAT Japan Warranty", exact=True
        )
        main_heading.wait_for(state="visible")

        section_headings = [
            "What Does the SAT Japan Warranty Cover?",
            "How Much Are You Covered For?",
            "How to Report an Issue",
            "SAT Japan Warranty vs. Marine Insurance",
            "Frequently Asked Questions",
        ]
        for heading in section_headings:
            self.page.get_by_role(
                "heading", name=heading, exact=True
            ).first.wait_for(state="attached")

        return {
            "path": urlparse(self.page.url).path,
            "heading": main_heading.inner_text().strip(),
            "sections": section_headings,
        }

    def verify_coverage_items(self):
        cards = self.page.locator(".grid---warrant-card .item--card")
        card_texts = [
            text.strip()
            for text in cards.locator("p.para").all_inner_texts()
        ]
        assert card_texts == self.COVERAGE_ITEMS
        assert cards.count() == len(self.COVERAGE_ITEMS)
        for index in range(cards.count()):
            assert_image_loaded(
                cards.nth(index).locator("img"),
                f"Warranty coverage icon {index + 1}",
            )
        return card_texts

    def verify_coverage_limits(self):
        table = self.page.locator("table").first
        table.scroll_into_view_if_needed()
        rows = [
            " ".join(text.split())
            for text in table.locator("tr").all_inner_texts()
        ]
        assert rows == [
            "Vehicle FOB Price Maximum Coverage",
            "FOB Price Below $500 Up to $210",
            (
                "FOB Price Between $501 and $3,999 "
                "Up to the Original FOB Price"
            ),
            "FOB Price of $4,000 or More Up to $3,999",
        ]
        page_text = self.page.locator("body").inner_text()
        assert all(
            phrase in page_text
            for phrase in (
                "brake pads",
                "wiper blades",
                "batteries",
                "light bulbs",
                "tyres are not covered",
            )
        )
        return rows

    def verify_claim_process(self):
        for heading in self.CLAIM_HEADINGS:
            self.page.get_by_role(
                "heading", name=heading, exact=True
            ).wait_for(state="attached")

        body_text = self.page.locator("body").inner_text()
        required_claim_details = (
            "48 hours",
            "info@satjapan.com",
            "support@satjapan.com",
            "video evidence is mandatory",
            "written repair estimate",
            "Damage Report form",
            "Port's Report",
            "do not go ahead with any repairs",
            "2 to 3 business days",
            "evidence of completed repairs",
        )
        assert all(
            detail.lower() in body_text.lower()
            for detail in required_claim_details
        )
        return list(self.CLAIM_HEADINGS)

    def verify_warranty_insurance_difference(self):
        heading = self.page.get_by_role(
            "heading",
            name="SAT Japan Warranty vs. Marine Insurance",
            exact=True,
        )
        heading.scroll_into_view_if_needed()
        section_text = heading.locator("xpath=.." ).inner_text()
        required_points = (
            "catastrophic losses",
            "shipping vessel",
            "sea voyage",
            "begins after the vehicle has arrived",
            "do not overlap",
        )
        assert all(
            point.lower() in section_text.lower()
            for point in required_points
        )
        return True

    def open_visible_faqs(self):
        faq_heading = self.page.get_by_role(
            "heading", name="Frequently Asked Questions", exact=True
        )
        faq_heading.scroll_into_view_if_needed()
        questions = []
        answers = []
        for index, expected_question in enumerate(self.FAQ_QUESTIONS):
            buttons = self.page.get_by_role(
                "button",
                name=expected_question,
                exact=True,
            ).filter(visible=True)
            assert buttons.count() == 1, (
                f"Expected one visible Warranty FAQ for {expected_question!r}, "
                f"found {buttons.count()}."
            )
            button = buttons.first
            questions.append(" ".join(button.inner_text().split()))
            target = button.get_attribute("data-bs-target")
            assert target, "Warranty FAQ button has no answer target."
            button.click()
            panel = self.page.locator(target)
            panel.wait_for(state="visible")
            answer = " ".join(panel.inner_text().split())
            assert answer, f"Warranty FAQ {index + 1} has an empty answer."
            answers.append(answer)

        return {"questions": questions, "answers": answers}
