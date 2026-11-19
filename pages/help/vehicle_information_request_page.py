from urllib.parse import parse_qs, urlparse


class VehicleInformationRequestPage:
    SUBMISSION_PATH = "/store-request-a-car"

    def __init__(self, page):
        self.page = page

    def _form(self):
        form = self.page.locator(
            "form[action*='/store-request-a-car']"
        )
        form.wait_for(state="visible")
        return form

    def _submit_button(self):
        return self._form().get_by_role(
            "button", name="Send Inquiry", exact=True
        )

    def _wait_for_option(self, field_name, option_label):
        option = self._form().locator(
            f"[name='{field_name}'] option",
            has_text=option_label,
        )
        option.wait_for(state="attached")
        return option

    def get_heading(self):
        heading = self.page.get_by_role(
            "heading", name="Request Vehicle Information", exact=True
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
        form = self._form()
        required = form.locator("[required]")
        return [
            required.nth(index).get_attribute("name")
            for index in range(required.count())
        ]

    def get_popular_make_links(self):
        links = self.page.locator(".vehicle-make-list .vehicle-make-item")
        return [
            {
                "label": links.nth(index).inner_text().strip(),
                "path": urlparse(
                    links.nth(index).get_attribute("href")
                ).path,
            }
            for index in range(links.count())
        ]

    def select_make_and_get_models(self, make):
        form = self._form()
        self._wait_for_option("make", make)
        with self.page.expect_response(
            lambda response: (
                urlparse(response.url).path == "/get-options-filter"
                and parse_qs(urlparse(response.url).query).get("type")
                == ["models"]
            )
        ) as response_info:
            form.locator("[name='make']").select_option(label=make)

        if not response_info.value.ok:
            raise AssertionError(
                "Model loading failed with HTTP "
                f"{response_info.value.status}."
            )

        model = form.locator("[name='model']")
        model.locator("option").nth(1).wait_for(state="attached")
        return [
            text.strip()
            for text in model.locator("option").all_inner_texts()
            if text.strip() and text.strip() != "Select Model"
        ]

    def fill_form(self, data):
        form = self._form()
        models = self.select_make_and_get_models(data["make"])
        if data["model"] not in models:
            raise AssertionError(
                f"{data['model']!r} was not loaded for {data['make']!r}."
            )
        form.locator("[name='model']").select_option(label=data["model"])

        for field_name in (
            "body_type",
            "steering",
            "country",
            "min_year",
            "max_year",
            "min_price",
            "max_price",
            "min_mileage",
            "max_mileage",
        ):
            self._wait_for_option(field_name, data[field_name])
            form.locator(f"[name='{field_name}']").select_option(
                label=data[field_name]
            )

        form.locator("[name='email']").fill(data["email"])
        form.locator("[name='question']").fill(data["question"])
        return self

    def set_email(self, email):
        self._form().locator("[name='email']").fill(email)
        return self

    def get_selected_labels(self):
        form = self._form()
        return {
            field_name: form.locator(
                f"[name='{field_name}'] option:checked"
            ).inner_text().strip()
            for field_name in (
                "make",
                "model",
                "body_type",
                "steering",
                "country",
                "min_year",
                "max_year",
                "min_price",
                "max_price",
                "min_mileage",
                "max_mileage",
            )
        }

    def submit_invalid_without_server_write(
        self,
        field_names,
        click_count=1,
    ):
        form = self._form()
        submission_requests = []

        def block_submission(route):
            request = route.request
            if (
                urlparse(request.url).path == self.SUBMISSION_PATH
                and request.method == "POST"
            ):
                submission_requests.append(request)
                route.abort()
            else:
                route.continue_()

        self.page.route("**/store-request-a-car", block_submission)
        try:
            self._submit_button().click(click_count=click_count)
            self.page.wait_for_timeout(250)
            validation = {
                field_name: form.locator(
                    f"[name='{field_name}']"
                ).evaluate(
                    """
                    field => ({
                        valid: field.validity.valid,
                        value_missing: field.validity.valueMissing,
                        type_mismatch: field.validity.typeMismatch,
                        message: field.validationMessage,
                    })
                    """
                )
                for field_name in field_names
            }
        finally:
            self.page.unroute("**/store-request-a-car", block_submission)

        return {
            "validation": validation,
            "post_count": len(submission_requests),
        }

    def submit_and_get_success(self):
        with self.page.expect_response(
            lambda response: (
                urlparse(response.url).path == self.SUBMISSION_PATH
                and response.request.method == "POST"
            )
        ) as response_info:
            self._submit_button().click()

        response = response_info.value
        if response.status not in (200, 302):
            raise AssertionError(
                "Vehicle information request failed with HTTP "
                f"{response.status}."
            )

        self.page.wait_for_load_state("domcontentloaded")
        success = self.page.locator(
            ".toast-success:visible, .alert-success:visible"
        ).first
        success.wait_for(state="visible", timeout=10000)
        return {
            "status": response.status,
            "message": success.inner_text().strip(),
        }

    def get_submit_button_text(self):
        button = self._submit_button()
        button.wait_for(state="visible")
        return button.inner_text().strip()
