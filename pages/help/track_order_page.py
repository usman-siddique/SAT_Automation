class TrackOrderPage:
    PATH = "/track-your-order"
    SUBMISSION_PATH = "/process-tracking-order"
    NO_ORDER_MESSAGE = (
        "No order found with the provided order number and email address. "
        "Please check your details and try again."
    )

    def __init__(self, page):
        self.page = page

    def get_heading(self):
        heading = self.page.get_by_role(
            "heading", name="Track Your Order", exact=True
        )
        heading.wait_for(state="visible")
        return heading.inner_text().strip()

    def get_form_details(self):
        order_input = self.page.locator("input[name='order_no']")
        email_input = self.page.locator("input[name='email']")
        submit_button = self.page.get_by_role(
            "button", name="Submit", exact=True
        )
        return {
            "order_visible": order_input.is_visible(),
            "order_required": order_input.get_attribute("required")
            is not None,
            "email_visible": email_input.is_visible(),
            "email_required": email_input.get_attribute("required")
            is not None,
            "email_type": email_input.get_attribute("type"),
            "submit_visible": submit_button.is_visible(),
        }

    def get_client_validation(self, order_id, email, click_count=1):
        submission_requests = []

        def record_submission(request):
            if (
                request.method == "POST"
                and self.SUBMISSION_PATH in request.url
            ):
                submission_requests.append(request)

        self.page.on("request", record_submission)
        try:
            self.page.locator("input[name='order_no']").fill(order_id)
            self.page.locator("input[name='email']").fill(email)
            self.page.get_by_role(
                "button", name="Submit", exact=True
            ).click(click_count=click_count)
            self.page.wait_for_timeout(200)

            return {
                "order": self.page.locator(
                    "input[name='order_no']"
                ).evaluate(
                    """field => ({
                        valid: field.validity.valid,
                        value_missing: field.validity.valueMissing,
                        message: field.validationMessage,
                    })"""
                ),
                "email": self.page.locator("input[name='email']").evaluate(
                    """field => ({
                        valid: field.validity.valid,
                        value_missing: field.validity.valueMissing,
                        type_mismatch: field.validity.typeMismatch,
                        message: field.validationMessage,
                    })"""
                ),
                "post_count": len(submission_requests),
            }
        finally:
            self.page.remove_listener("request", record_submission)

    def submit_order_lookup(self, order_id, email):
        if not order_id:
            raise RuntimeError("TRACK_ORDER_ID is missing.")
        if not email:
            raise RuntimeError("TRACK_ORDER_EMAIL is missing.")

        self.page.locator("input[name='order_no']").fill(order_id)
        self.page.locator("input[name='email']").fill(email)
        self.page.get_by_role("button", name="Submit", exact=True).click()
        self.page.wait_for_url(f"**/tracking-order-summary/{order_id}*")
        self.page.get_by_role(
            "heading", name="Order Summary", exact=True
        ).wait_for(state="visible")
        return self

    def get_order_summary_heading(self):
        return self.page.get_by_role(
            "heading", name="Order Summary", exact=True
        ).inner_text().strip()

    def submit_invalid_lookup(self, order_id, email):
        self.page.locator("input[name='order_no']").fill(order_id)
        self.page.locator("input[name='email']").fill(email)
        with self.page.expect_response(
            lambda response: self.SUBMISSION_PATH in response.url
            and response.request.method == "POST"
        ):
            self.page.get_by_role(
                "button", name="Submit", exact=True
            ).click()
        message = self.page.get_by_text(self.NO_ORDER_MESSAGE, exact=True)
        message.wait_for(state="visible")
        return message.inner_text().strip()

    def has_order_id_label(self):
        return self.page.get_by_text("Order ID", exact=False).count() > 0

    def has_order_id_value(self, order_id):
        return self.page.get_by_text(order_id, exact=True).count() > 0
