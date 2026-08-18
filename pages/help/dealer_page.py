class DealerPage:
    def __init__(self, page):
        self.page = page

    def get_anonymous_login_controls(self):
        email = self.page.locator("#login_email")
        email.wait_for(state="visible")
        continue_button = self.page.get_by_role(
            "button", name="Continue", exact=True
        )
        continue_button.wait_for(state="visible")
        return {
            "email_placeholder": email.get_attribute("placeholder"),
            "continue_enabled": continue_button.is_enabled(),
        }
