from urllib.parse import urlparse


class InquiryFormPage:
    REQUIRED_FIELDS = ("name", "email", "question")
    VALIDATION_ERRORS = {
        "name": ".name-error-text",
        "email": ".email-error-text",
        "question": ".question-error-text",
    }

    def __init__(self, page):
        self.page = page

    def _form(self):
        form = self.page.locator("#formInquiry")
        form.wait_for(state="visible")
        return form

    def _submit_button(self):
        return self._form().get_by_role(
            "button", name="Send Inquiry", exact=True
        )

    def get_heading(self):
        heading = self.page.get_by_role(
            "heading", name="Inquiry Form:", exact=True
        )
        heading.wait_for(state="visible")
        return heading.inner_text().strip()

    def get_visible_field_names(self):
        form = self._form()
        fields = form.locator("input:visible, select:visible, textarea:visible")
        return [
            fields.nth(index).get_attribute("name")
            for index in range(fields.count())
            if fields.nth(index).get_attribute("name")
        ]

    def get_required_field_names(self):
        required = []
        form = self._form()
        for field_name in self.REQUIRED_FIELDS:
            field = form.locator(f"[name='{field_name}']")
            label = field.locator("xpath=preceding::label[1]")
            if label.locator("span.text-danger", has_text="*").count():
                required.append(field_name)
        return required

    def fill_form(self, data, omitted_field=None):
        form = self._form()

        for field_name in ("name", "email"):
            if field_name != omitted_field:
                form.locator(f"[name='{field_name}']").fill(data[field_name])

        phone = data.get("phone")
        if phone:
            form.locator("[name='phone']").fill(phone)

        country = form.locator("[name='country']")
        country.select_option(label=data["country"])

        city = form.locator("[name='city']")
        city.locator("option", has_text=data["city"]).wait_for(
            state="attached"
        )
        city.select_option(label=data["city"])

        if omitted_field != "question":
            form.locator("[name='question']").fill(data["question"])

        return self

    def submit_and_get_success(self):
        with self.page.expect_response(
            lambda response: (
                urlparse(response.url).path == "/store-inquiry"
                and response.request.method == "POST"
            )
        ) as response_info:
            self._submit_button().click()

        response = response_info.value
        if not response.ok:
            raise AssertionError(
                f"Inquiry submission failed with HTTP {response.status}."
            )

        result = response.json()
        message = str(result.get("message", "")).strip()
        if result.get("status") is not True or not message:
            raise AssertionError(
                f"Inquiry submission returned an unexpected response: {result}"
            )

        self.page.get_by_text(message, exact=True).last.wait_for(
            state="visible", timeout=3000
        )
        return result

    def submit_and_get_validation(self, field_name):
        if field_name not in self.VALIDATION_ERRORS:
            raise ValueError(f"Unsupported required field: {field_name}")

        submission_requests = []

        def capture_submission(request):
            if (
                urlparse(request.url).path == "/store-inquiry"
                and request.method == "POST"
            ):
                submission_requests.append(request)

        self.page.on("request", capture_submission)
        self._submit_button().click()

        error = self._form().locator(self.VALIDATION_ERRORS[field_name])
        error.wait_for(state="visible")
        message = error.inner_text().strip()
        self.page.wait_for_timeout(250)

        if submission_requests:
            raise AssertionError(
                "The invalid Inquiry Form unexpectedly called /store-inquiry."
            )
        return message

    def submit_and_get_invalid_email_validation(self):
        return self.submit_and_get_validation("email")

    def get_submit_button_text(self):
        button = self._submit_button()
        button.wait_for(state="visible")
        return button.inner_text().strip()
