# ============================================================
# pages/car_services/non_stolen_vehicle_page.py
# Contains the NonStolenVehiclePage class.
# Handles Non Stolen Vehicle Check page and form submission.
# ============================================================

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class NonStolenVehiclePage:
    def __init__(self, page):
        self.page = page


    # ============================================================
    # Verify: Page heading
    # ============================================================

    def verify_page_heading(self):
        heading = self.page.locator("h1.title-stolen:has-text('Steps to get a Non-Stolen Verification Certificate')")
        if not heading.is_visible():
            raise AssertionError("Page heading not visible")
        print(f"✅ Page heading verified: {heading.inner_text()}")


    # ============================================================
    # Click Begin Verification button to open modal
    # ============================================================

    def open_modal(self):
        self.page.locator("button[data-bs-target='#nonStolenVehicle']").click()
        self.page.locator("#nonStolenVehicle").wait_for(state="visible")
        print("✅ Modal opened")


    # ============================================================
    # Close modal
    # ============================================================

    def close_modal(self):
        close_btn = self.page.locator("#nonStolenVehicle .btn-close")
        if close_btn.is_visible():
            close_btn.click()
            self.page.wait_for_timeout(500)
        print("✅ Modal closed")


    # ============================================================
    # Enter Stock ID and verify auto-filled car details
    # ============================================================

    def enter_stock_id(self, stock_id):
        stock_input = self.page.locator("#stock_id")
        stock_input.fill(stock_id)
        stock_input.press("Enter")
        
        # Wait for either car details or error message
        self.page.wait_for_function(
            "document.querySelector('#car_name')?.innerText?.trim() !== '' || "
            "document.querySelector('#stockInfo .text-danger')?.offsetParent !== null",
            timeout=30000
        )
        
        return self


    # ============================================================
    # Get stock ID error message
    # ============================================================

    def get_stock_id_error(self):
        error = self.page.locator("#stockInfo .text-danger")
        error.wait_for(state="visible", timeout=5000)
        return error.inner_text()


    # ============================================================
    # Verify car details are loaded
    # ============================================================

    def verify_car_details_loaded(self):
        # Wait for car name to be populated
        self.page.wait_for_function(
            "document.querySelector('#car_name')?.innerText?.trim() !== ''",
            timeout=30000
        )
        car_name = self.page.locator("#car_name").inner_text()
        # Check if error message appears instead
        if self.page.locator("#stockInfo .text-danger").is_visible():
            raise AssertionError(f"Stock ID error: {self.page.locator('#stockInfo .text-danger').inner_text()}")
        assert car_name.strip() != "", "Car details not loaded"
        print(f"✅ Car details loaded: {car_name}")


    # ============================================================
    # Fill personal information
    # ============================================================

    def fill_personal_info(self, full_name="", email="", phone="", select_country=True, message=""):
        # Full Name
        if full_name:
            self.page.locator("#name").fill(full_name)
        
        # Email
        if email:
            self.page.locator("#email").fill(email)
        
        # Phone - click country code dropdown
        if select_country:
            country_dropdown = self.page.locator(".iti__selected-country")
            country_dropdown.click()
            self.page.wait_for_timeout(500)
            
            # Search for United Kingdom
            search_input = self.page.locator(".iti__search-input")
            if search_input.is_visible():
                search_input.fill("United Kingdom")
                self.page.wait_for_timeout(500)
            
            # Select United Kingdom from results
            self.page.locator(".iti__country-list .iti__country:has-text('United Kingdom')").click()
        
        # Enter phone number
        if phone:
            self.page.locator("#call_phone").fill(phone)
        
        # Message (optional)
        if message:
            self.page.locator("#message").fill(message)
        
        print(f"✅ Personal info filled")
        return self


    # ============================================================
    # Get phone error message (country code missing)
    # ============================================================

    def get_phone_error(self):
        error = self.page.locator(".call_phone-error-text")
        if error.is_visible():
            return error.inner_text()
        return None


    # ============================================================
    # Fill payment details using Stripe Elements
    # ============================================================

    def fill_payment_details(self, card_number="", expiry="", cvc="", zip_code=""):
        # Switch to Stripe iframe
        stripe_iframe = self.page.frame_locator("iframe[title='Secure card payment input frame']")
        
        # Card number
        if card_number:
            card_input = stripe_iframe.locator("input[name='cardnumber']")
            card_input.wait_for(state="visible", timeout=30000)
            card_input.fill(card_number)
        
        # Expiry date
        if expiry:
            expiry_input = stripe_iframe.locator("input[name='exp-date']")
            expiry_input.fill(expiry)
        
        # CVC
        if cvc:
            cvc_input = stripe_iframe.locator("input[name='cvc']")
            cvc_input.fill(cvc)
        
        # ZIP code
        if zip_code:
            zip_input = stripe_iframe.locator("input[name='postal']")
            zip_input.fill(zip_code)
        
        print(f"✅ Payment details filled")
        return self


    # ============================================================
    # Get payment error message from toast
    # ============================================================

    def get_payment_error(self):
        toast = self.page.locator(".toast-body")
        toast.wait_for(state="visible")
        return toast.inner_text().strip()


    # ============================================================
    # Submit the form
    # ============================================================

    def submit_form(self):
        self.page.locator("#submitNonStolen").click()
        print("✅ Form submitted")
        return self


    # ============================================================
    # Check if submission was successful (modal closes)
    # ============================================================

    def is_submission_successful(self):
        self.page.wait_for_selector("#nonStolenVehicle", state="hidden")
        return not self.page.locator("#nonStolenVehicle").is_visible()