from urllib.parse import urlparse


class DealerPage:
    ACCOUNT_STATE_HEADINGS = (
        "Create an Account",
        "Become a Dealer Today",
        "You Already Have a Dealer Account",
        "Your Dealer Account is Under Review",
        "Your Dealer Account Was Rejected",
    )
    CREATE_FORM_PATH = "/dealers/dealer-signup-process"
    JOIN_FORM_PATH = "/dealers/join-as-dealer"

    def __init__(self, page):
        self.page = page

    def get_account_state_heading(self):
        for name in self.ACCOUNT_STATE_HEADINGS:
            heading = self.page.get_by_role("heading", name=name, exact=True)
            if heading.is_visible():
                return heading.inner_text().strip()
        return None

    def get_create_account_form(self):
        form = self._create_form()
        form.wait_for(state="visible")
        fields = form.locator("input:visible, select:visible, textarea:visible")
        next_button = form.get_by_role("button", name="Next", exact=True)
        next_button.wait_for(state="visible")
        return {
            "fields": [
                fields.nth(index).get_attribute("name")
                for index in range(fields.count())
            ],
            "next_enabled": next_button.is_enabled(),
        }

    def _create_form(self):
        return self.page.locator("#dealer-create-form")

    def _join_form(self):
        return self.page.get_by_role(
            "button", name="Submit", exact=True
        ).locator("xpath=ancestor::form[1]")

    def get_create_account_step_two(self):
        form = self._create_form()
        heading = self.page.get_by_role(
            "heading", name="Additional Information", exact=True
        )
        heading.wait_for(state="visible")
        return {
            "fields": [
                name
                for name in (
                    "annual_revenue",
                    "annual_imports",
                    "password",
                    "conform_password",
                    "email_marketing",
                )
                if form.locator(f"[name='{name}']").count()
            ],
            "create_button": form.get_by_role(
                "button", name="Create account", exact=True
            ).inner_text().strip(),
        }

    def fill_create_account_details(self, data):
        form = self._create_form()
        form.locator("#dealer-email").fill(data["email"])
        form.locator("#dealer-name").fill(data["name"])
        form.locator("#dealer-phone").fill(data["phone"])
        form.locator("#company-name").fill(data["company"])
        form.locator("#your-position").fill(data["position"])
        return self

    def wait_for_create_account_next(self):
        button = self._create_form().get_by_role(
            "button", name="Next", exact=True
        )
        self.page.wait_for_function(
            "() => !document.querySelector('#create-section-next').disabled",
            timeout=20000,
        )
        return button

    def open_create_account_step_two(self):
        self.wait_for_create_account_next().click()
        self.page.get_by_role(
            "heading", name="Additional Information", exact=True
        ).wait_for(state="visible")
        return self

    def click_create_next_without_server_write(self, click_count=1):
        attempts = []

        def block_submission(route):
            attempts.append(route.request)
            route.abort()

        pattern = "**/dealers/dealer-signup-process*"
        self.page.route(pattern, block_submission)
        try:
            self.wait_for_create_account_next().click(
                click_count=click_count
            )
            self.page.wait_for_timeout(300)
        finally:
            self.page.unroute(pattern, block_submission)
        return attempts

    def get_email_validation_message(self):
        field = self._create_form().locator("#dealer-email")
        return field.evaluate("element => element.validationMessage")

    def enter_existing_dealer_email(self, email):
        form = self._create_form()
        form.locator("#dealer-email").fill(email)
        form.locator("#dealer-email").blur()
        message = self.page.get_by_text(
            "Dealer email already exists.", exact=True
        )
        message.wait_for(state="visible", timeout=10000)
        return message.inner_text().strip()

    def fill_create_account_passwords(self, password, confirmation=None):
        form = self._create_form()
        form.locator("#password").fill(password)
        form.locator("#conform_password").fill(
            confirmation if confirmation is not None else password
        )
        return self

    def submit_create_account(self):
        self._create_form().get_by_role(
            "button", name="Create account", exact=True
        ).click()
        heading = self.page.get_by_role(
            "heading",
            name="Your Dealer Account is Under Review",
            exact=True,
        )
        heading.wait_for(state="visible", timeout=30000)
        return heading.inner_text().strip()

    def click_create_account_without_server_write(self):
        attempts = []

        def block_submission(route):
            attempts.append(route.request)
            route.abort()

        pattern = "**/dealers/dealer-signup-process*"
        self.page.route(pattern, block_submission)
        try:
            self._create_form().get_by_role(
                "button", name="Create account", exact=True
            ).click()
            self.page.wait_for_timeout(300)
        finally:
            self.page.unroute(pattern, block_submission)
        return attempts

    def get_join_form(self):
        form = self._join_form()
        form.wait_for(state="visible")
        fields = form.locator("input:visible")
        return {
            "fields": [
                fields.nth(index).get_attribute("name")
                for index in range(fields.count())
                if fields.nth(index).get_attribute("name")
            ],
            "email_disabled": form.locator("#email").is_disabled(),
            "submit_enabled": form.get_by_role(
                "button", name="Submit", exact=True
            ).is_enabled(),
        }

    def fill_join_form(self, data):
        form = self._join_form()
        form.locator("#full_name").fill(data["name"])

        country_button = form.locator(".iti__selected-country")
        if "No country selected" in country_button.inner_text():
            country_button.click()
            self.page.locator(
                ".iti__country[data-country-code='pk']"
            ).click()

        form.locator("#phone").fill(data["phone"])
        form.locator("#dealership_name").fill(data["dealership"])
        form.locator("#position").fill(data["position"])
        form.locator("#website").fill(data["website"])
        return self

    def submit_join_form(self):
        self._join_form().get_by_role(
            "button", name="Submit", exact=True
        ).click()
        heading = self.page.get_by_role(
            "heading",
            name="Your Dealer Account is Under Review",
            exact=True,
        )
        heading.wait_for(state="visible", timeout=30000)
        return heading.inner_text().strip()

    def click_join_submit_without_server_write(self):
        attempts = []

        def block_submission(route):
            attempts.append(route.request)
            route.abort()

        self.page.route("**/dealers/join-as-dealer*", block_submission)
        try:
            self._join_form().get_by_role(
                "button", name="Submit", exact=True
            ).click()
            self.page.wait_for_timeout(300)
        finally:
            self.page.unroute("**/dealers/join-as-dealer*", block_submission)
        return attempts

    def current_path(self):
        return urlparse(self.page.url).path

    def is_main_dealer_link_visible(self):
        menu = self.page.locator("p.cnm-cls", has_text="Help").first.locator(
            ".."
        )
        menu.hover()
        link = menu.locator(".dropdown_content_header").get_by_role(
            "link", name="Become a SAT Japan Dealer", exact=True
        )
        return link.is_visible()
