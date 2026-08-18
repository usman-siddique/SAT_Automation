class TrackOrderPage:
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

    def submit_order_lookup(self, order_id, email):
        if not order_id:
            raise RuntimeError("TRACK_ORDER_ID is missing.")
        if not email:
            raise RuntimeError("LOGIN_EMAIL is missing.")

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

    def submit_mismatched_email(self, order_id, email):
        self.page.locator("input[name='order_no']").fill(order_id)
        self.page.locator("input[name='email']").fill(email)
        self.page.get_by_role("button", name="Submit", exact=True).click()
        message = self.page.get_by_text(self.NO_ORDER_MESSAGE, exact=True)
        message.wait_for(state="visible")
        return message.inner_text().strip()

    def has_order_id_label(self):
        return self.page.get_by_text("Order ID", exact=False).count() > 0
