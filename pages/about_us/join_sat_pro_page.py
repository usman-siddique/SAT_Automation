# ============================================================
# pages/about_us/join_sat_pro_page.py
# Handles Join SAT Pro page flow.
# Supports both membership states:
# - Non-member: Join button leads to login/payment.
# - Existing member: active SAT Pro benefits page is verified.
# ============================================================

import sys
import os
import re
import time
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import BASE_URL
from pages.auth.login_page import LoginPage


class JoinSatProPage:
    def __init__(self, page):
        self.page = page

    def _active_heading(self):
        return self.page.get_by_role(
            "heading",
            name=re.compile(r"You.?re a SAT Pro!?", re.IGNORECASE),
        ).first

    def _join_button(self):
        # The site has rendered this action as both an anchor and a button.
        # Its exact user-visible label is the stable contract.
        return self.page.get_by_text(
            "Join SAT Pro",
            exact=True,
        ).filter(visible=True).first

    def _payment_heading(self):
        return self.page.locator(
            "h2.payment-card-title:has-text('Payment Details')"
        ).first

    def _wait_for_sat_pro_state(self, timeout=30000):
        """Return the first real SAT Pro state rendered by the application."""
        deadline = time.monotonic() + (timeout / 1000)

        while time.monotonic() < deadline:
            if self._active_heading().is_visible():
                return "active"
            if self._payment_heading().is_visible() or "sat-pro-payment" in self.page.url:
                return "payment"
            if self._join_button().is_visible():
                return "join"
            if self.page.locator("#login_email").is_visible() or "/login" in self.page.url:
                return "login"
            self.page.wait_for_timeout(250)

        raise AssertionError(
            "SAT Pro page did not render an active membership, Join button, "
            "payment page, or login page within 30 seconds"
        )


    # ============================================================
    # Navigation: Go to SAT Pro page directly via URL
    # ============================================================

    def go_to_sat_pro(self):
        self.page.goto(f"{BASE_URL}/sat-pro", wait_until="domcontentloaded")
        state = self._wait_for_sat_pro_state()
        assert state in ("active", "join"), (
            f"Unexpected SAT Pro landing state: {state}"
        )
        print(f"✅ Navigation to SAT Pro ({state} membership state): PASS")
        return state


    # ============================================================
    # Helper: Click Join SAT Pro button
    # ============================================================

    def click_join_button(self):
        btn = self._join_button()
        btn.wait_for(state="visible")
        btn.click()


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
    # Verify: Existing SAT Pro membership page
    # ============================================================

    def verify_active_pro_page(self):
        heading = self._active_heading()
        heading.wait_for(state="visible")
        assert heading.is_visible(), "❌ Active SAT Pro heading not visible"

        place_order = self.page.get_by_text("Place an Order", exact=True).first
        assert place_order.is_visible(), "❌ Place an Order action not visible"

        benefits = self.page.get_by_text("SAT Pro Benefits", exact=True).first
        assert benefits.is_visible(), "❌ SAT Pro Benefits section not visible"

        print("✅ Existing SAT Pro membership page verified")


    def _verify_post_join_state(self):
        state = self._wait_for_sat_pro_state()
        if state == "active":
            self.verify_active_pro_page()
            return
        if state == "payment":
            self.verify_payment_page()
            return
        raise AssertionError(f"Unexpected state after joining SAT Pro: {state}")


    # ============================================================
    # Flow: Logged out
    # Anonymous context clicks Join → redirects to /login → logs in.
    # After login, verifies either an existing active membership or
    # the payment page offered to a non-member.
    # ============================================================

    def flow_logged_out(self):
        state = self.go_to_sat_pro()

        if state == "active":
            self.verify_active_pro_page()
            return

        self.click_join_button()
        state = self._wait_for_sat_pro_state()
        assert state == "login", "❌ Join SAT Pro did not redirect to /login"
        print("✅ Redirected to login page")

        LoginPage(self.page).login()
        state = self.go_to_sat_pro()
        if state == "active":
            self.verify_active_pro_page()
            return

        self.click_join_button()
        self._verify_post_join_state()


    # ============================================================
    # Flow: Logged in
    # Navigate to /sat-pro and verify the account's real membership state.
    # ============================================================

    def flow_logged_in(self):
        state = self.go_to_sat_pro()
        if state == "active":
            self.verify_active_pro_page()
            return

        self.click_join_button()
        self._verify_post_join_state()
