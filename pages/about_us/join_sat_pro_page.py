# ============================================================
# pages/about_us/join_sat_pro_page.py
# Handles Join SAT Pro page flow.
# Two states: logged out (redirects to login first)
#             logged in (goes directly to payment page)
# ============================================================

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import BASE_URL
from pages.auth.login_page import LoginPage


class JoinSatProPage:
    def __init__(self, page):
        self.page = page


    # ============================================================
    # Navigation: Go to SAT Pro page directly via URL
    # ============================================================

    def go_to_sat_pro(self):
        self.page.goto(f"{BASE_URL}/sat-pro", wait_until="domcontentloaded")
        self.page.locator(".satpro-paid-bannar h2.title").wait_for(state="visible")
        print("✅ Navigation to Join SAT Pro: PASS")


    # ============================================================
    # Helper: Click Join SAT Pro button
    # ============================================================

    def click_join_button(self):
        btn = self.page.locator("a.btn-sat-pro:has-text('Join SAT Pro')")
        btn.wait_for(state="visible")
        btn.click()


    # ============================================================
    # Helper: Check if currently logged in
    # ============================================================

    def _is_logged_in(self):
        try:
            sign_in = self.page.locator("header").get_by_role("link", name="Sign in")
            return not sign_in.is_visible(timeout=3000)
        except:
            return False


    # ============================================================
    # Verify: Payment page elements
    # PayPal buttons load inside an iframe
    # ============================================================

    def verify_payment_page(self):
        self.page.locator("h2.payment-card-title:has-text('Payment Details')").wait_for(state="visible")
        assert self.page.locator("h2.payment-card-title:has-text('Payment Details')").is_visible(), \
            "❌ Payment Details heading not visible"

        self.page.locator("h3.sat-pro-ben-title:has-text('Become a PRO and Start Saving Today')").wait_for(state="visible")
        assert self.page.locator("h3.sat-pro-ben-title:has-text('Become a PRO and Start Saving Today')").is_visible(), \
            "❌ SAT Pro benefits heading not visible"

        assert self.page.locator("h3.user-profile-title").is_visible(), \
            "❌ User name not visible on payment page"

        assert self.page.locator("p.user-profile-email").is_visible(), \
            "❌ User email not visible on payment page"

        assert self.page.locator("span.badge.bg-blue-50").is_visible(), \
            "❌ Master Level badge not visible on payment page"

        print("✅ SAT Pro payment page verified")


    # ============================================================
    # Flow: Logged out
    # If session is already active (from previous test), skips login
    # and goes directly to payment page verification.
    # If truly logged out, clicks Join → redirects to /login →
    # logs in → navigates back to /sat-pro → clicks Join again
    # ============================================================

    def flow_logged_out(self):
        self.go_to_sat_pro()

        if self._is_logged_in():
            print("⚠️ Session already active - skipping login redirect step")
            # Wait for page to be stable before clicking Join again
            self.page.wait_for_load_state("networkidle")
            self.click_join_button()
        else:
            self.click_join_button()
            self.page.locator("#login_email").wait_for(state="visible")
            assert "login" in self.page.url, "❌ Join SAT Pro did not redirect to /login"
            print("✅ Redirected to login page")
            LoginPage(self.page).login()
            self.go_to_sat_pro()
            self.click_join_button()

        self.page.wait_for_url("**/sat-pro-payment", wait_until="domcontentloaded")
        self.verify_payment_page()


    # ============================================================
    # Flow: Logged in
    # Navigate to /sat-pro → click Join → verify payment page
    # ============================================================

    def flow_logged_in(self):
        # Wait for any pending redirects to finish after login
        self.page.wait_for_load_state("networkidle")
        self.go_to_sat_pro()
        self.click_join_button()
        self.page.wait_for_url("**/sat-pro-payment", wait_until="domcontentloaded")
        self.verify_payment_page()