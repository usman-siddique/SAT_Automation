import re
from urllib.parse import urlparse


class SellerRegistrationPage:
    SUBMISSION_PATH = "/seller-registration"
    STEPS = {
        1: "Company",
        2: "Contact & seller information",
        3: "Verification",
    }

    def __init__(self, page):
        self.page = page

    def _form(self):
        form = self.page.locator("#sellerApplicationForm")
        form.wait_for(state="visible")
        return form

    def _active_section(self):
        section = self._form().locator(
            ".seller-step-section:not(.d-none)"
        )
        section.wait_for(state="visible")
        return section

    def get_stepper_labels(self):
        return [
            text.strip()
            for text in self.page.locator(
                ".seller-stepper-label"
            ).all_inner_texts()
        ]

    def switch_language(self, language, expected_path):
        selector = self.page.locator("#sellerLangSwitch")
        selector.wait_for(state="visible")
        selected = selector.locator("option:checked").inner_text().strip()
        if selected != language:
            selector.select_option(label=language)
            self.page.wait_for_url(f"**{expected_path}")
            self._form()
        return self

    def get_selected_language(self):
        return self.page.locator(
            "#sellerLangSwitch option:checked"
        ).inner_text().strip()

    def current_path(self):
        return urlparse(self.page.url).path

    def get_active_step(self):
        return int(self._active_section().get_attribute("data-step-index"))

    def get_active_heading(self):
        return self._active_section().locator(
            ".seller-step-title"
        ).inner_text().strip()

    def get_active_field_names(self):
        fields = self._active_section().locator(
            "input[name], select[name], textarea[name]"
        )
        return [
            fields.nth(index).get_attribute("name")
            for index in range(fields.count())
            if fields.nth(index).get_attribute("name") != "_token"
        ]

    def get_visible_error_messages(self):
        errors = self._active_section().locator(
            ".seller-field-group.has-error [data-required-error]"
        )
        return [
            text.strip()
            for text in errors.all_inner_texts()
            if text.strip()
        ]

    def _capture_post_while(self, action):
        posts = []

        def capture(request):
            if (
                request.method == "POST"
                and urlparse(request.url).path == self.SUBMISSION_PATH
            ):
                posts.append(request)

        self.page.on("request", capture)
        try:
            action()
            self.page.wait_for_timeout(250)
        finally:
            self.page.remove_listener("request", capture)
        return posts

    def continue_without_submission(self):
        section = self._active_section()
        posts = self._capture_post_while(
            lambda: section.locator("[data-step-continue]").click()
        )
        return {
            "step": self.get_active_step(),
            "errors": self.get_visible_error_messages(),
            "post_count": len(posts),
        }

    def submit_invalid_without_server_write(self):
        section = self._active_section()
        posts = self._capture_post_while(
            lambda: section.locator("[data-step-submit]").click()
        )
        return {
            "step": self.get_active_step(),
            "errors": self.get_visible_error_messages(),
            "post_count": len(posts),
        }

    def fill_company(self, data, include_website=True):
        form = self._form()
        form.locator("[name='company_name']").fill(data["company_name"])
        form.locator("[name='country']").select_option(data["country"])
        form.locator("[name='registration_number']").fill(
            data["registration_number"]
        )
        if include_website:
            form.locator("[name='website']").fill(data["website"])
        return self

    def fill_seller_information(self, data, email=None):
        form = self._form()
        form.locator("[name='contact_name']").fill(data["contact_name"])
        form.locator("[name='email']").fill(
            data["email"] if email is None else email
        )
        form.locator("[name='phone_number']").fill(data["phone_number"])
        form.locator("[name='seller_type']").select_option(
            data["seller_type"]
        )
        form.locator("[name='monthly_availability']").select_option(
            data["monthly_availability"]
        )
        form.locator("[name='vehicle_location[]']").select_option(
            data["vehicle_locations"]
        )
        for vehicle_type in data["vehicle_types"]:
            self._active_section().get_by_role(
                "button", name=vehicle_type, exact=True
            ).click()
        return self

    def set_phone_number(self, phone_number):
        phone = self._form().locator("[name='phone_number']")
        phone.fill(phone_number)
        self.page.wait_for_function(
            """
            () => {
                const input = document.querySelector('#seller_phone_number');
                const api = window.intlTelInput;
                const instance = api && api.getInstance
                    ? api.getInstance(input)
                    : null;
                return instance && instance.isValidNumber() !== null;
            }
            """,
            timeout=15000,
        )
        return self

    def continue_to_next_step(self):
        current_step = self.get_active_step()
        self._active_section().locator("[data-step-continue]").click()
        next_step = self._form().locator(
            f".seller-step-section[data-step-index='{current_step + 1}']"
        )
        next_step.wait_for(state="visible")
        return self

    def go_back(self):
        current_step = self.get_active_step()
        self._active_section().locator("[data-step-back]").click()
        previous = self._form().locator(
            f".seller-step-section[data-step-index='{current_step - 1}']"
        )
        previous.wait_for(state="visible")
        return self

    def get_company_values(self):
        form = self._form()
        return {
            "company_name": form.locator(
                "[name='company_name']"
            ).input_value(),
            "country": form.locator("[name='country']").input_value(),
            "registration_number": form.locator(
                "[name='registration_number']"
            ).input_value(),
            "website": form.locator("[name='website']").input_value(),
        }

    def upload_document(self, file_path):
        self._form().locator("#companyDocInput").set_input_files(file_path)
        self.page.locator("#companyDocPreview").wait_for(state="visible")
        return self

    def upload_invalid_type(self):
        message = "Please upload a PDF, JPG or PNG file."
        self._form().locator("#companyDocInput").set_input_files(
            {
                "name": "seller-registration.txt",
                "mimeType": "text/plain",
                "buffer": b"invalid seller document",
            }
        )
        self.page.get_by_text(message, exact=True).last.wait_for(
            state="visible"
        )
        return message

    def upload_oversized_document(self):
        message = "File size must be under 10 MB."
        self._form().locator("#companyDocInput").set_input_files(
            {
                "name": "oversized-seller-document.png",
                "mimeType": "image/png",
                "buffer": b"0" * (10 * 1024 * 1024 + 1),
            }
        )
        self.page.get_by_text(message, exact=True).last.wait_for(
            state="visible"
        )
        return message

    def get_document_preview(self):
        preview = self.page.locator("#companyDocPreview")
        preview.wait_for(state="visible")
        return {
            "name": preview.locator("#companyDocName").inner_text().strip(),
            "meta": preview.locator("#companyDocMeta").inner_text().strip(),
        }

    def remove_document(self):
        self.page.locator("#companyDocRemove").click()
        self.page.locator("#companyDocDropzone").wait_for(state="visible")
        return self._form().locator("#companyDocInput").input_value()

    def confirm_agreement(self):
        self._form().locator("#agreementCheckbox").check()
        return self

    def submit_and_get_result(self):
        with self.page.expect_response(
            lambda response: (
                urlparse(response.url).path == self.SUBMISSION_PATH
                and response.request.method == "POST"
            )
        ) as response_info:
            self._active_section().locator("[data-step-submit]").click()

        response = response_info.value
        if not response.ok:
            raise AssertionError(
                f"Seller application failed with HTTP {response.status}."
            )

        heading = self.page.get_by_role(
            "heading", name="Application Submitted", exact=True
        )
        heading.wait_for(state="visible", timeout=30000)
        application_id = self.page.get_by_text(
            re.compile(r"^SEL-\d+$")
        ).inner_text().strip()
        status = self.page.get_by_text("Under Review", exact=True)
        status.wait_for(state="visible")
        return {
            "heading": heading.inner_text().strip(),
            "application_id": application_id,
            "status": status.inner_text().strip(),
            "return_visible": self.page.get_by_role(
                "link", name="Return to SAT Japan", exact=True
            ).is_visible(),
        }
