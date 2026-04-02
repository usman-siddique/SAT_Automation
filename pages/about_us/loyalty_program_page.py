# ============================================================
# pages/about_us/loyalty_program_page.py
# Handles Loyalty Program page verifications.
# Two states: logged out and logged in.
# ============================================================

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import BASE_URL


class LoyaltyProgramPage:
    def __init__(self, page):
        self.page = page


    # ============================================================
    # Navigation: Go to Loyalty Program via About Us hover menu
    # Scoped to About Us parent to avoid footer link conflicts
    # ============================================================

    def go_to_loyalty_program(self):
        # Use direct URL navigation to avoid hover menu flakiness
        self.page.goto(f"{BASE_URL}/loyalty-program", wait_until="domcontentloaded")
        self.page.locator("h2.heading-sat-pro:has-text('Unlock More Benefits With Our Loyalty Program')").wait_for(state="visible")
        print("✅ Navigation to Loyalty Program: PASS")


    # ============================================================
    # Verify: Logged out state
    # Heading and Sign Up button visible
    # Sign Up click redirects to /login
    # ============================================================

    def verify_logged_out_state(self):
        heading = self.page.locator("h2.heading-sat-pro:has-text('Unlock More Benefits With Our Loyalty Program')")
        heading.wait_for(state="visible")
        assert heading.is_visible(), "❌ Logged out heading not visible"

        sign_up_btn = self.page.locator("a.sign-up-free:has-text('Sign Up - It\\'s Free')")
        sign_up_btn.wait_for(state="visible")
        assert sign_up_btn.is_visible(), "❌ Sign Up button not visible"

        sign_up_btn.click()
        self.page.locator("#login_email").wait_for(state="visible")
        assert "login" in self.page.url, "❌ Sign Up did not redirect to /login"

        print("✅ Loyalty Program logged out state verified")


    # ============================================================
    # Verify: Logged in state
    # Navigate directly via URL after login
    # Welcome message, heading, and all 4 benefit cards visible
    # ============================================================

    def verify_logged_in_state(self):
        # Wait for login to fully complete
        self.page.get_by_role("link", name="Sell My Car").wait_for(state="visible")
        self.page.wait_for_load_state("networkidle")

        # Use hover menu navigation — carries session correctly unlike goto
        menu = self.page.locator("p.cnm-cls:has-text('About Us')").locator("..")
        menu.hover()
        link = menu.locator(".dropdown_content_header").get_by_role("link", name="Loyalty Program")
        link.wait_for(state="visible")
        link.click()
        self.page.wait_for_url("**/loyalty-program", wait_until="domcontentloaded")

        # Welcome message - dynamic text, verify it contains expected static part
        welcome = self.page.locator("h2.login-sat-user")
        welcome.wait_for(state="visible")
        assert welcome.is_visible(), "❌ Welcome message not visible"
        assert "you're at" in welcome.inner_text(), "❌ Welcome message does not contain expected text"
        print(f"✅ Welcome message verified: {welcome.inner_text().strip()}")

        # Logged in main heading
        heading = self.page.locator("h2.heading-sat-pro:has-text('Buy More For Less With Master')")
        heading.wait_for(state="visible")
        assert heading.is_visible(), "❌ Logged in heading not visible"

        # All 4 benefit cards with their badges
        cards = [
            (".benfit-card-more:has-text('Create an account')", "span:has-text('Master Level 1')"),
            (".benfit-card-more:has-text('Make two orders in two years')", "span:has-text('Master Level 2')"),
            (".benfit-card-more:has-text('Make five orders in five years')", "span:has-text('Master Level 3')"),
            (".benfit-card-more:has-text('Make a monthly payment of 19.99$')", "span:has-text('SAT Pro')"),
        ]

        for card_locator, badge_locator in cards:
            card = self.page.locator(card_locator)
            card.wait_for(state="visible")
            assert card.is_visible(), f"❌ Benefit card not visible: {card_locator}"
            badge = card.locator(badge_locator)
            assert badge.is_visible(), f"❌ Badge not visible: {badge_locator}"

        print("✅ Loyalty Program logged in state verified")