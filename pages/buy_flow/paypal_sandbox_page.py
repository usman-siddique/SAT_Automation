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
        body_text = self.page.locator("body").inner_text()
        amounts = re.findall(r"[¥￥]\s*[0-9,]+", body_text)
        expected = self._normalize_price(expected_total_jpy)
        assert any(self._normalize_price(amount) == expected for amount in amounts), (
            "PayPal total does not match the converted SAT total: expected "
            f"{expected_total_jpy}, PayPal displayed {amounts}."
        )
        print(f"PayPal JPY total verified: {expected_total_jpy}")

    def login_and_approve(
        self,
        email: str | None,
        password: str | None,
        expected_total_jpy: str,
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
        self.page.wait_for_url("**/new-car-order-summary/**", timeout=120000)
        print("PayPal payment approved and returned to SAT")
        return self
