# ============================================================
# pages/auth/login_page.py
# Contains the LoginPage class for handling login flow.
# Called from conftest.py during browser setup.
# ============================================================

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import BASE_URL, LOGIN_EMAIL, LOGIN_PASSWORD


class LoginPage:
    def __init__(self, page):
        self.page = page

    # ============================================================
    # Action: Login to the site
    # ============================================================

    def login(self):
        # Go to site
        self.page.goto(BASE_URL, wait_until="domcontentloaded")

        # Check if already logged in (Sign in button NOT visible)
        sign_in_btn = self.page.locator("header").get_by_role("link", name="Sign in")
        if not sign_in_btn.is_visible(timeout=3000):
            print("✅ Already logged in, skipping login")
            return

        # Click Sign in button
        sign_in_btn.click()

        # Wait for email field
        self.page.locator("#login_email").wait_for(state="visible")
        for c in LOGIN_EMAIL:
            self.page.locator("#login_email").type(c, delay=10)

        self.page.get_by_role("button", name="Continue").click()

        # Wait for password field
        self.page.locator("input[type='password']").wait_for(state="visible")
        for c in LOGIN_PASSWORD:
            self.page.locator("input[type='password']").type(c, delay=20)

        self.page.get_by_role("button", name="Login").click()

        # Wait for Sell My Car link to confirm login success
        self.page.get_by_role("link", name="Sell My Car").wait_for(state="visible")

        # Wait for all redirects to fully complete before any navigation
        self.page.wait_for_load_state("networkidle")

        print("✅ Login: PASS")