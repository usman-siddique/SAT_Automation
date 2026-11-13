from urllib.parse import urlparse


class InquiryFormPage:
    REQUIRED_MARKERS = ("name", "email", "question")
    VALIDATION_ERRORS = {
        "name": ".name-error-text",
        "email": ".email-error-text",
        "phone": ".phone-error",
        "country": ".country-error-text",
        "city": ".city-error-text",
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
        for field_name in self.REQUIRED_MARKERS:
            field = form.locator(f"[name='{field_name}']")
            label = field.locator("xpath=preceding::label[1]")
            if label.locator("span.text-danger", has_text="*").count():
                required.append(field_name)
        return required

    def fill_form(self, data):
        form = self._form()

        for field_name in ("name", "email"):
            form.locator(f"[name='{field_name}']").fill(data[field_name])

        phone = data.get("phone")
        if phone:
            form.locator("[name='phone']").fill(phone)

        self.select_country_and_city(data["country"], data["city"])
        form.locator("[name='question']").fill(data["question"])

        return self

    def set_field_value(self, field_name, value):
        field = self._form().locator(f"[name='{field_name}']")
        if field_name in ("country", "city"):
            if value:
                field.select_option(label=value)
            else:
                field.select_option(label="Select")
        else:
            field.fill(value)
        return self

    def select_country_and_get_cities(self, country):
        form = self._form()
        with self.page.expect_response(
            lambda response: (
                urlparse(response.url).path == "/get-ports-by-country"
                and response.request.method == "GET"
            )
        ) as response_info:
            form.locator("[name='country']").select_option(label=country)

        if not response_info.value.ok:
            raise AssertionError(
                "Destination city loading failed with HTTP "
                f"{response_info.value.status}."
            )

        city = form.locator("[name='city']")
        city.locator("option").nth(1).wait_for(state="attached")
        return [
            text.strip()
            for text in city.locator("option").all_inner_texts()
            if text.strip() and text.strip() != "Select"
        ]

    def select_country_and_city(self, country, city):
        cities = self.select_country_and_get_cities(country)
        if city not in cities:
            raise AssertionError(
                f"{city!r} was not loaded for destination {country!r}."
            )
        self._form().locator("[name='city']").select_option(label=city)
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

    def submit_and_get_validation(self, field_names):
        unsupported = set(field_names) - set(self.VALIDATION_ERRORS)
        if unsupported:
            raise ValueError(
                f"Unsupported validation fields: {sorted(unsupported)}"
            )
        submission_requests = []

        def block_submission(route):
            request = route.request
            if (
                urlparse(request.url).path == "/store-inquiry"
                and request.method == "POST"
            ):
                submission_requests.append(request)
                route.abort()
            else:
                route.continue_()

        self.page.route("**/store-inquiry", block_submission)
        try:
            self._submit_button().click()
            messages = {}
            for field_name in field_names:
                error = self._form().locator(
                    self.VALIDATION_ERRORS[field_name]
                )
                error.wait_for(state="visible")
                messages[field_name] = error.inner_text().strip()
            self.page.wait_for_timeout(250)
        finally:
            self.page.unroute("**/store-inquiry", block_submission)

        return {
            "errors": messages,
            "post_count": len(submission_requests),
        }

    def get_submit_button_text(self):
        button = self._submit_button()
        button.wait_for(state="visible")
        return button.inner_text().strip()
