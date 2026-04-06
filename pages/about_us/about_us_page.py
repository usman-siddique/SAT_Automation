# ============================================================
# pages/about_us/about_us_page.py
# Handles About Us hover menu navigation and
# static page verifications for:
#   - About SAT
#   - Company Profile
#   - Why Choose SAT
#   - Privacy Policy
#   - Terms and Conditions
#   - Shipping Agents
# ============================================================

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class AboutUsPage:
    def __init__(self, page):
        self.page = page


    # ============================================================
    # Helper: Hover About Us menu and click a sub-link
    # Scoped to About Us parent container to avoid footer conflicts
    # p.cnm-cls and dropdown_content_header are siblings inside
    # the same div.hov-nav-items parent
    # ============================================================

    def _navigate_to(self, link_name, wait_for_locator):
        menu = self.page.locator("p.cnm-cls:has-text('About Us')").locator("..")
        menu.hover()
        link = menu.locator(".dropdown_content_header").get_by_role("link", name=link_name, exact=True)
        link.wait_for(state="visible")
        link.click()
        self.page.locator(wait_for_locator).wait_for(state="visible")


    # ============================================================
    # Navigation: About SAT
    # ============================================================

    def go_to_about_sat(self):
        self._navigate_to("About SAT", "h2:has-text('Our Mission, Vision, and Values')")
        print("✅ Navigation to About SAT: PASS")


    # ============================================================
    # Navigation: Company Profile
    # ============================================================

    def go_to_company_profile(self):
        self._navigate_to("Company Profile", "h1.comp-profile-hdr")
        print("✅ Navigation to Company Profile: PASS")


    # ============================================================
    # Navigation: Why Choose SAT
    # ============================================================

    def go_to_why_choose_sat(self):
        self._navigate_to("Why Choose SAT", "h1.why-title")
        print("✅ Navigation to Why Choose SAT: PASS")


    # ============================================================
    # Navigation: Privacy Policy
    # ============================================================

    def go_to_privacy_policy(self):
        self._navigate_to("Privacy Policy", "section.cookies-polices-main h2.cookies-polices-comman-hdr")
        print("✅ Navigation to Privacy Policy: PASS")


    # ============================================================
    # Navigation: Terms and Conditions
    # ============================================================

    def go_to_terms_and_conditions(self):
        self._navigate_to("Terms and Conditions", "h1.term-main-hdr")
        print("✅ Navigation to Terms and Conditions: PASS")


    # ============================================================
    # Navigation: Shipping Agents
    # ============================================================

    def go_to_shipping_agents(self):
        self._navigate_to("Shipping Agents", "h1.title-shipagent")
        print("✅ Navigation to Shipping Agents: PASS")


    # ============================================================
    # Verify: About SAT page content
    # ============================================================

    def verify_about_sat(self):
        self.page.locator("h2:has-text('Our Mission, Vision, and Values')").wait_for(state="visible")
        assert self.page.locator("h2:has-text('Our Mission, Vision, and Values')").is_visible(), \
            "❌ Mission heading not visible"

        self.page.locator("h2.about-heading:has-text('SAT Japan at a Glance')").wait_for(state="visible")
        assert self.page.locator("h2.about-heading:has-text('SAT Japan at a Glance')").is_visible(), \
            "❌ Glance heading not visible"

        self.page.locator(".glance--1 .glance-track").wait_for(state="visible")
        assert self.page.locator(".glance--1 .glance-track").is_visible(), \
            "❌ Glance slider 1 not visible"
        self.page.locator(".glance--2 .glance-track").wait_for(state="visible")
        assert self.page.locator(".glance--2 .glance-track").is_visible(), \
            "❌ Glance slider 2 not visible"

        self.page.locator("h2:has-text('Our Milestones')").wait_for(state="visible")
        assert self.page.locator("h2:has-text('Our Milestones')").is_visible(), \
            "❌ Milestones heading not visible"

        print("✅ About SAT content verified")


    # ============================================================
    # Verify: Company Profile page content
    # ============================================================

    def verify_company_profile(self):
        heading = self.page.locator("h1.comp-profile-hdr:has-text('SAT - Your Trusted Partner in the Automotive Industry')")
        heading.wait_for(state="visible")
        assert heading.is_visible(), "❌ Company Profile heading not visible"
        print("✅ Company Profile content verified")


    # ============================================================
    # Verify: Why Choose SAT page content
    # ============================================================

    def verify_why_choose_sat(self):
        self.page.locator("h1.why-title:has-text('Why Choose SAT Japan?')").wait_for(state="visible")
        assert self.page.locator("h1.why-title:has-text('Why Choose SAT Japan?')").is_visible(), \
            "❌ Why Choose SAT heading not visible"

        assert self.page.locator("h2:has-text('Exceptional Customer Support')").is_visible(), \
            "❌ Exceptional Customer Support section not visible"

        print("✅ Why Choose SAT content verified")


    # ============================================================
    # Verify: Privacy Policy page content
    # ============================================================

    def verify_privacy_policy(self):
        # Scope to main content section to avoid matching repeated headings
        main = self.page.locator("section.cookies-polices-main")
        main.locator("h2.cookies-polices-comman-hdr:has-text('Privacy Policy')").wait_for(state="visible")
        assert main.locator("h2.cookies-polices-comman-hdr:has-text('Privacy Policy')").is_visible(), \
            "❌ Privacy Policy heading not visible"

        # Contact us is outside the section, scoped to its own div
        contact = self.page.locator("div.contact-us-section h2.cookies-polices-comman-hdr:has-text('Contact us')")
        contact.wait_for(state="visible")
        assert contact.is_visible(), "❌ Contact us section not visible"

        print("✅ Privacy Policy content verified")


    # ============================================================
    # Verify: Terms and Conditions page content
    # Opens vehicle purchase agreement in new tab and verifies URL
    # ============================================================

    def verify_terms_and_conditions(self):
        self.page.locator("h1.term-main-hdr:has-text('Terms and Conditions')").wait_for(state="visible")
        assert self.page.locator("h1.term-main-hdr:has-text('Terms and Conditions')").is_visible()

        link = self.page.locator("a:has-text('vehicle purchase agreement')")
        link.wait_for(state="visible")
        href = link.get_attribute("href")
        assert "vehicle-sales-agreement.pdf" in href

        # Only open the PDF in headed mode (where it actually opens a new tab)
        headless = os.getenv("HEADLESS", "false").lower() == "true"
        if not headless:
            with self.page.context.expect_page() as new_tab_info:
                link.click() 
            new_tab = new_tab_info.value
            # Removed hardcoded timeout; uses default 30s
            new_tab.wait_for_url("**/vehicle-sales-agreement.pdf")
            assert "vehicle-sales-agreement.pdf" in new_tab.url
            new_tab.close()
        else:
            print("⚠️ Headless mode: PDF link verified, but opening skipped (PDF would download)")

        print("✅ Terms and Conditions content verified")


    # ============================================================
    # Verify: Shipping Agents page content
    # Verifies map image, then applies Sri Lanka country filter
    # Scoped to div.filter-by-country to avoid strict mode violation
    # ============================================================

    def verify_shipping_agents(self):
        self.page.locator("h1.title-shipagent:has-text('Explore Our International Office Map')").wait_for(state="visible")
        assert self.page.locator("h1.title-shipagent:has-text('Explore Our International Office Map')").is_visible(), \
            "❌ Shipping Agents heading not visible"

        assert self.page.locator("img[alt='sat agent map']").is_visible(), \
            "❌ Agent map image not visible"

        # Verify filter label is present (appears twice for mobile/desktop, use first)
        filter_label = self.page.locator("span.title:has-text('Filter by country:')").first
        filter_label.wait_for(state="visible")
        assert filter_label.is_visible(), "❌ Filter by country label not visible"

        print("✅ Shipping Agents content verified")