"""Page object for the SAT Non-Stolen Vehicle Check service."""

from urllib.parse import urlparse

from pages.car_services.image_assertions import assert_image_loaded


class NonStolenVehiclePage:
    PROCESS_STEPS = [
        "Start by clicking on the 'Begin Verification' button below.",
        (
            "Fill in the details in the pop-up that comes and make a payment "
            "of 30,000 YEN. Alternatively, you can send an email to "
            "info@satjapan.com and our support team will reach out to you and "
            "guide you about the next steps."
        ),
        (
            "After your details have been submitted, the verification through "
            "relevant agencies will take 5-8 working days."
        ),
        (
            "Soon after, your verification will be dispatched to your local "
            "address through Japan's postal code."
        ),
    ]

    PAYMENT_ENDPOINTS = (
        "/non_stolen/stripe-payment-intent",
        "/non_stolen/non-stolen-credit-card",
    )

    def __init__(self, page):
        self.page = page

    @staticmethod
    def _clean(text):
        return " ".join(text.split())

    @staticmethod
    def _assert_image_loaded(image, description):
        assert_image_loaded(image, description)

    @property
    def modal(self):
        return self.page.locator("#nonStolenVehicle")

    def verify_overview_and_process(self):
        hero_heading = self.page.get_by_role(
            "heading",
            name=(
                "Get a verified non-stolen vehicle certificate with our "
                "Non-Stolen Vehicle Check Service"
            ),
            exact=True,
        )
        hero_heading.wait_for(state="visible")

        banner = self.page.locator("img.nsb__bg")
        banner.wait_for(state="visible")
        self._assert_image_loaded(banner, "Non-Stolen Vehicle banner")

        body_text = self._clean(self.page.locator("body").inner_text())
        required_details = (
            "advanced stolen car checking procedure",
            "inspection certificate to confirm the status of your vehicle",
            "30,000 YEN",
            "5-8 working days",
        )
        assert all(
            detail.lower() in body_text.lower()
            for detail in required_details
        )

        process_heading = self.page.get_by_role(
            "heading",
            name="Steps to get a Non-Stolen Verification Certificate",
            exact=True,
        )
        process_heading.scroll_into_view_if_needed()
        process_list = process_heading.locator("xpath=following-sibling::ol[1]")
        steps = [
            self._clean(process_list.locator("li").nth(index).inner_text())
            for index in range(process_list.locator("li").count())
        ]
        assert steps == self.PROCESS_STEPS

        help_email = self.page.locator(
            ".need-help-card a[href='mailto:info@satjapan.com']"
        )
        assert help_email.is_visible()
        return {
            "path": urlparse(self.page.url).path,
            "heading": self._clean(hero_heading.inner_text()),
            "steps": steps,
        }

    def open_modal(self):
        self.page.get_by_role(
            "button", name="Begin Verification", exact=True
        ).click()
        self.modal.wait_for(state="visible")

        heading = self.modal.get_by_role(
            "heading", name="SAT Non Stolen Form", exact=True
        )
        assert heading.is_visible()
        assert (
            "Enter the Stock ID of the car"
            in self._clean(self.modal.inner_text())
        )
        return self

    def verify_form_contract(self):
        required_controls = (
            "#stock_id",
            "#email",
            "#call_phone",
            "#message",
            "#submitNonStolen",
        )
        assert all(
            self.modal.locator(selector).is_visible()
            for selector in required_controls
        )

        payment_heading = self.modal.get_by_role(
            "heading", name="Make Payment of 30,000 YEN", exact=True
        )
        payment_heading.scroll_into_view_if_needed()
        stripe_logo = self.modal.locator("img[alt='stripe_logo']")
        self._assert_image_loaded(stripe_logo, "Stripe logo")

        card_frame = self.modal.frame_locator(
            "iframe[title='Secure card payment input frame']"
        )
        card_frame.locator("input[name='cardnumber']").wait_for(
            state="visible", timeout=30000
        )

    def lookup_stock(self, stock_id):
        stock_input = self.modal.locator("#stock_id")
        stock_input.fill(stock_id)
        self.page.wait_for_function(
            """
            () => {
                const name = document.querySelector('#car_name')
                    ?.textContent?.trim();
                const error = document.querySelector('#stockInfo')
                    ?.textContent?.trim();
                return Boolean(name || error);
            }
            """,
            timeout=30000,
        )

        error = self._clean(
            self.modal.locator("#stockInfo").inner_text()
        )
        if error:
            return {"error": error}

        fields = {
            "name": "#car_name",
            "year": "#car_year",
            "engine": "#car_engine",
            "mileage": "#car_mileage",
            "transmission": "#car_transmission",
        }
        details = {
            key: self._clean(self.modal.locator(selector).inner_text())
            for key, selector in fields.items()
        }
        assert all(details.values()), "One or more vehicle details are empty."
        assert self.modal.locator("#car_id").input_value().strip()
        service_fee = self._clean(
            self.modal.locator(".service-fee").inner_text()
        )
        assert "Service Fee:" in service_fee
        assert "30,000 YEN" in service_fee
        assert stock_input.input_value().lower() == stock_id.lower()
        return details

    def fill_valid_submission(self, submission_data):
        self.modal.locator("#name").fill(submission_data["full_name"])
        self.modal.locator("#email").fill(submission_data["email"])

        phone_input = self.modal.locator("#call_phone")
        phone_input.evaluate(
            """
            (element, country) => {
                const instance = window.intlTelInputGlobals.getInstance(element);
                instance.setCountry(country);
            }
            """,
            submission_data["phone_country"],
        )
        phone_input.fill(submission_data["phone"])
        self.modal.locator("#message").fill(
            "Automated Non-Stolen Vehicle verification payment test."
        )

        card = submission_data["payment_card"]
        card_frame = self.modal.frame_locator(
            "iframe[title='Secure card payment input frame']"
        )
        card_frame.locator("input[name='cardnumber']").fill(card["number"])
        card_frame.locator("input[name='exp-date']").fill(card["expiry"])
        card_frame.locator("input[name='cvc']").fill(card["cvc"])
        postal = card_frame.locator("input[name='postal']")
        if postal.count() > 0:
            postal.fill(card["postal_code"])

        return {
            "email": self.modal.locator("#email").input_value(),
            "phone": phone_input.input_value(),
            "card_last_four": card["number"].replace(" ", "")[-4:],
        }

    def submit_and_verify_payment(self):
        self.page.evaluate(
            "sessionStorage.removeItem('payment_succeeded')"
        )

        intent_capture = {}
        submission_capture = {}
        intent_pattern = "**/non_stolen/stripe-payment-intent*"
        submission_pattern = "**/non_stolen/non-stolen-credit-card*"

        def capture_json_response(route, request, capture):
            if request.method != "POST":
                route.continue_()
                return
            upstream = route.fetch()
            capture["http_status"] = upstream.status
            capture["payload"] = upstream.json()
            route.fulfill(response=upstream)

        def capture_intent(route, request):
            capture_json_response(route, request, intent_capture)

        def capture_submission(route, request):
            capture_json_response(route, request, submission_capture)

        # Capture the response before the success handler reloads the page.
        # route.fetch sends the original request once; fulfill reuses that
        # response and does not create a duplicate payment.
        self.page.route(intent_pattern, capture_intent)
        self.page.route(submission_pattern, capture_submission)

        try:
            with self.page.expect_response(
                lambda response: (
                    "/non_stolen/stripe-payment-intent" in response.url
                    and response.request.method == "POST"
                ),
                timeout=90000,
            ):
                with self.page.expect_response(
                    lambda response: (
                        "/non_stolen/non-stolen-credit-card" in response.url
                        and response.request.method == "POST"
                    ),
                    timeout=90000,
                ):
                    self.modal.locator("#submitNonStolen").click()
        finally:
            self.page.unroute(intent_pattern, capture_intent)
            self.page.unroute(submission_pattern, capture_submission)

        assert "payload" in intent_capture, (
            "Stripe payment-intent response was not captured before reload."
        )
        assert "payload" in submission_capture, (
            "Non-Stolen submission response was not captured before reload."
        )

        assert 200 <= intent_capture["http_status"] < 300, (
            "Stripe payment-intent request failed with HTTP "
            f"{intent_capture['http_status']}."
        )
        assert 200 <= submission_capture["http_status"] < 300, (
            "Non-Stolen submission failed with HTTP "
            f"{submission_capture['http_status']}."
        )

        intent_payload = intent_capture["payload"]
        assert isinstance(intent_payload, dict), intent_payload
        assert intent_payload.get("status") is True, intent_payload
        submission_payload = submission_capture["payload"]
        assert isinstance(submission_payload, dict), submission_payload
        assert submission_payload.get("status") is True, submission_payload
        self.modal.wait_for(state="hidden", timeout=30000)
        return {
            "intent_status": intent_payload["status"],
            "submission_status": submission_payload["status"],
            "submission_http_status": submission_capture["http_status"],
            "page_url": self.page.url,
        }

    def verify_negative_validation(self, valid_stock_id, invalid_stock_id):
        payment_requests = []

        def track_payment_request(request):
            if any(
                endpoint in request.url
                for endpoint in self.PAYMENT_ENDPOINTS
            ):
                payment_requests.append(request.url)

        self.page.on("request", track_payment_request)
        try:
            invalid_result = self.lookup_stock(invalid_stock_id)
            assert invalid_result == {"error": "Stock ID not found."}

            self.modal.locator("#stock_id").fill("")
            self.modal.locator("#email").fill("")
            self.modal.locator("#call_phone").fill("")
            self.modal.locator("#submitNonStolen").click()

            stock_error = self.modal.locator(".stock_id-error-text")
            email_error = self.modal.locator(".email-error-text")
            phone_error = self.modal.locator(".call_phone-error-text")
            assert self._clean(stock_error.inner_text()) == (
                "This field is required"
            )
            assert self._clean(email_error.inner_text()) == (
                "This field is required"
            )
            assert self._clean(phone_error.inner_text()) in {
                "Phone is required",
                "Please select country code",
            }

            self.lookup_stock(valid_stock_id)
            self.modal.locator("#email").fill("invalid-email")
            self.modal.locator("#submitNonStolen").click()
            assert self._clean(email_error.inner_text()) == (
                "Enter valid email."
            )
            assert payment_requests == [], (
                "Validation unexpectedly initiated a payment request."
            )
        finally:
            self.page.remove_listener("request", track_payment_request)

        return {
            "invalid_stock": "Stock ID not found.",
            "required_stock": "This field is required",
            "required_email": "This field is required",
            "invalid_email": "Enter valid email.",
            "payment_requests": payment_requests,
        }
