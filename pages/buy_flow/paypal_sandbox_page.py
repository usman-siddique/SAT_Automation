import re
from urllib.parse import urlparse

from playwright.sync_api import Page


class PayPalSandboxPage:
    """PayPal-owned page used by User, Guest, or Dealer payment journeys."""

    def __init__(self, page: Page):
        self.page = page

    @staticmethod
    def _normalize_price(price_text: str):
        normalized = re.sub(r"[^0-9.]", "", price_text)
        if not normalized:
            raise AssertionError(f"Price value was not found in: {price_text!r}")
        return normalized

    def _verify_sandbox_url(self):
        hostname = (urlparse(self.page.url).hostname or "").lower()
        assert hostname == "sandbox.paypal.com" or hostname.endswith(
            ".sandbox.paypal.com"
        ), f"Expected PayPal sandbox, found {self.page.url}"

    def _verify_jpy_total(self, expected_total_jpy: str):
        expected = self._normalize_price(expected_total_jpy)
        displayed_amounts = []

        for _ in range(30):
            body_text = self.page.locator("body").inner_text()
            displayed_amounts = re.findall(r"[0-9][0-9,]*(?:\.[0-9]+)?", body_text)
            if any(
                self._normalize_price(amount) == expected
                for amount in displayed_amounts
            ):
                print(f"PayPal JPY total verified: {expected_total_jpy}")
                return
            self.page.wait_for_timeout(1000)

        raise AssertionError(
            "PayPal total does not match the converted SAT total after a "
            f"30-second wait: expected {expected_total_jpy}, PayPal displayed "
            f"{displayed_amounts}."
        )

    def login_and_approve(
        self,
        email: str | None,
        password: str | None,
        expected_total_jpy: str,
        return_url_pattern: str = "**/new-car-order-summary/**",
    ):
        """Authenticate the sandbox buyer, verify JPY, and approve payment."""
        if not email or not password:
            raise RuntimeError(
                "PayPal sandbox credentials are missing. Set "
                "PAYPAL_SANDBOX_EMAIL and PAYPAL_SANDBOX_PASSWORD in .env."
            )

        self.page.wait_for_load_state("domcontentloaded")
        self._verify_sandbox_url()

        email_input = self.page.locator("#email")
        if email_input.is_visible(timeout=5000):
            email_input.fill(email)
            next_button = self.page.locator("#btnNext")
            if next_button.is_visible():
                next_button.click()

            password_input = self.page.locator("#password")
            password_input.wait_for(state="visible", timeout=30000)
            password_input.fill(password)
            self.page.locator("#btnLogin").click()
            print("PayPal sandbox buyer logged in")
        else:
            print("PayPal sandbox buyer session already authenticated")

        approve = self.page.locator("#payment-submit-btn")
        if not approve.is_visible(timeout=5000):
            approve = self.page.get_by_role(
                "button",
                name=re.compile(
                    r"Continue\s+to\s+Review\s+Order|Review\s+Order|"
                    r"注文.*確認|続行",
                    re.IGNORECASE,
                ),
            ).first
        approve.wait_for(state="visible", timeout=60000)
        assert approve.is_enabled(), "PayPal approval button is disabled"
        self._verify_jpy_total(expected_total_jpy)

        approve.click()
        self.page.wait_for_url(return_url_pattern, timeout=120000)
        print("PayPal payment approved and returned to SAT")
        return self
