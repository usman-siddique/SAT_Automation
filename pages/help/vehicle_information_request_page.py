class VehicleInformationRequestPage:
    def __init__(self, page):
        self.page = page

    def get_heading(self):
        heading = self.page.get_by_role(
            "heading", name="Request Vehicle Information", exact=True
        )
        heading.wait_for(state="visible")
        return heading.inner_text().strip()

    def get_visible_field_names(self):
        form = self.page.locator("form:visible").first
        fields = form.locator("input:visible, select:visible, textarea:visible")
        return [
            fields.nth(index).get_attribute("name")
            for index in range(fields.count())
            if fields.nth(index).get_attribute("name")
        ]

    def get_required_field_names(self):
        form = self.page.locator("form:visible").first
        required = form.locator("[required]")
        return [
            required.nth(index).get_attribute("name")
            for index in range(required.count())
        ]

    def get_empty_form_validation_messages(self):
        form = self.page.locator("form:visible").first
        if form.evaluate("form => form.checkValidity()"):
            return {}

        required = form.locator("[required]")
        return {
            required.nth(index).get_attribute("name"): required.nth(
                index
            ).evaluate("field => field.validationMessage")
            for index in range(required.count())
        }

    def get_submit_button_text(self):
        button = self.page.locator("form:visible").first.get_by_role(
            "button", name="Send Inquiry", exact=True
        )
        button.wait_for(state="visible")
        return button.inner_text().strip()
