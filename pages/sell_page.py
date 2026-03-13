# ============================================================
# pages/sell_page.py
# Contains the SellPage class for the Sell My Car page.
# Covers all 3 tabs: Price Quote, List on SAT, Auction with SAT
#
# Uses domcontentloaded for faster page loads
# Uses wait_for(state="visible") for specific elements
# ============================================================

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import BASE_URL, IMAGES


# ============================================================
# Helper: Dropdown Selector
# Used by all forms that have custom dropdowns
# ============================================================

def select_dropdown(page, list_id, value):
    dropdown = page.locator(f"ul#{list_id}")
    dropdown.locator("..").locator("button.satSelectBtn").click()

    # Wait for the dropdown list to be visible before searching for the item
    dropdown.wait_for(state="visible")

    item = dropdown.get_by_text(value, exact=True)

    # Wait for the item to be present in DOM before scrolling
    # Uses default 30s timeout - succeeds as soon as item is ready
    item.wait_for(state="visible")
    item.scroll_into_view_if_needed()

    item.click()


# ============================================================
# Page Class: Sell My Car Page
# ============================================================

class SellPage:
    def __init__(self, page):
        self.page = page


    # ============================================================
    # Navigation: Go to Sell Page
    # ============================================================

    def go_to_sell_page(self):
        self.page.get_by_role("link", name="Sell My Car").click()

        # Handle "Leave Page" modal if it appears (shown when navigating away from incomplete form)
        try:
            leave_btn = self.page.locator("#leave_page")
            leave_btn.wait_for(state="visible", timeout=3000)
            leave_btn.click()
        except:
            pass  # Modal did not appear, continue normally

        # Wait for Get Price Quote link to confirm page loaded
        self.page.get_by_role("link", name="Get Price Quote").wait_for(state="visible")


    # ============================================================
    # Positive Test: Get Price Quote - All 3 Steps
    # ============================================================

    def get_price_quote(self, step1_data, step2_data, step3_data):

        # ----- Step 1: Basic Car Details -----
        self.page.get_by_role("link", name="Get Price Quote").click()
        self.page.wait_for_load_state("domcontentloaded")

        # Wait for dropdown button to be ready
        self.page.locator("ul#year_list").locator("..").locator("button.satSelectBtn").wait_for(state="visible")

        select_dropdown(self.page, "year_list", step1_data["year"])
        select_dropdown(self.page, "make_list", step1_data["make"])

        # Wait for model dropdown to be populated after make selection
        self.page.wait_for_function("document.querySelectorAll('#make_model_list li').length > 1")

        select_dropdown(self.page, "make_model_list", step1_data["model"])
        self.page.locator("#model_code").fill(step1_data["model_code"])

        self.page.get_by_role("button", name="Continue").click()

        # Wait for step 2 mileage field to confirm step 2 loaded
        self.page.locator("#mileage").wait_for(state="visible")

        print("✅ Get Price Quote Step 1: PASS")

        # ----- Step 2: Additional Car Details -----
        self.page.locator("#mileage").fill(step2_data["mileage"])
        self.page.locator("#engine").fill(step2_data["engine"])
        select_dropdown(self.page, "color_list", step2_data["color"])
        select_dropdown(self.page, "condition_list", step2_data["condition"])
        select_dropdown(self.page, "car_keys_list", step2_data["keys"])
        select_dropdown(self.page, "original_owner_list", step2_data["original_owner"])

        self.page.set_input_files("#imageInput", IMAGES["mitsubishi"])
        self.page.wait_for_timeout(2000)

        self.page.get_by_role("button", name="Continue").click()

        # Wait for phone field to confirm step 3 loaded
        self.page.locator("#phone").wait_for(state="visible")

        print("✅ Get Price Quote Step 2: PASS")

        # ----- Step 3: Personal Information -----
        self.page.locator("#phone").fill(step3_data["phone"])
        self.page.locator("#check_terms_policy").check()

        self.page.get_by_role("button", name="Submit Quote Request").click()
        self.page.wait_for_url("**/get-price-quote-success")

        assert "get-price-quote-success" in self.page.url, "❌ Get Price Quote: Success page URL not found"
        assert self.page.get_by_text("Your Instant Quote Request Has Been Submitted!").is_visible(), "❌ Get Price Quote: Success message not visible"

        print("✅ Get Price Quote Step 3: PASS")

        # Navigate back to sell page
        self.page.goto(f"{BASE_URL}/sell", wait_until="domcontentloaded")
        self.page.get_by_role("link", name="Get Price Quote").wait_for(state="visible")


    # ============================================================
    # Negative Test 1: Get Price Quote - Step 1 All Fields Empty
    # Expected: Year, Make, Model error messages all appear
    # ============================================================

    def get_price_quote_validation(self):
        self.page.get_by_role("link", name="Get Price Quote").click()
        self.page.wait_for_load_state("domcontentloaded")

        # Wait for Continue button to be ready
        self.page.locator("ul#year_list").locator("..").locator("button.satSelectBtn").wait_for(state="visible")

        # Click Continue without filling anything
        self.page.get_by_role("button", name="Continue").click()

        # Assert all 3 error messages are visible
        assert self.page.locator("#year_err_msg").is_visible(), "❌ Year error message not visible"
        assert self.page.locator("#make_err_msg").is_visible(), "❌ Make error message not visible"
        assert self.page.locator("#make_model_err_msg").is_visible(), "❌ Model error message not visible"

        # Assert correct error text for each field
        assert self.page.locator("#year_err_msg").inner_text() == "This field is required", "❌ Year error text incorrect"
        assert self.page.locator("#make_err_msg").inner_text() == "This field is required", "❌ Make error text incorrect"
        assert self.page.locator("#make_model_err_msg").inner_text() == "This field is required", "❌ Model error text incorrect"

        print("❎ Negative Test 1 - All Fields Empty: Year, Make, Model errors correctly shown")


    # ============================================================
    # Negative Test 2: Get Price Quote - Step 1 Partial Validation
    # Year filled, Make and Model left empty
    # Expected: Only Make and Model errors appear, Year error hidden
    # ============================================================

    def get_price_quote_partial_validation(self, step1_data):
        self.page.get_by_role("link", name="Get Price Quote").click()
        self.page.wait_for_load_state("domcontentloaded")

        # Wait for Continue button to be ready
        self.page.locator("ul#year_list").locator("..").locator("button.satSelectBtn").wait_for(state="visible")

        # Fill only Year, leave Make and Model empty
        select_dropdown(self.page, "year_list", step1_data["year"])

        self.page.get_by_role("button", name="Continue").click()

        # Assert Make and Model errors are visible
        assert self.page.locator("#make_err_msg").is_visible(), "❌ Make error message not visible"
        assert self.page.locator("#make_model_err_msg").is_visible(), "❌ Model error message not visible"

        # Assert Year error is NOT visible (year was filled correctly)
        assert not self.page.locator("#year_err_msg").is_visible(), "❌ Year error should not be visible"

        print("❎ Negative Test 2 - Partial Fields: Make and Model errors shown, Year error correctly hidden")


    # ============================================================
    # Negative Test 3: Get Price Quote - Step 3 Terms Checkbox Unchecked
    # All fields filled correctly but terms checkbox left unchecked
    # Expected: Terms error message appears
    # ============================================================

    def get_price_quote_terms_validation(self, step1_data, step2_data, step3_data):

        # ----- Step 1: Basic Car Details -----
        self.page.get_by_role("link", name="Get Price Quote").click()
        self.page.wait_for_load_state("domcontentloaded")

        # Wait for dropdown button to be ready
        self.page.locator("ul#year_list").locator("..").locator("button.satSelectBtn").wait_for(state="visible")

        select_dropdown(self.page, "year_list", step1_data["year"])
        select_dropdown(self.page, "make_list", step1_data["make"])

        # Wait for model dropdown to be populated after make selection
        self.page.wait_for_function("document.querySelectorAll('#make_model_list li').length > 1")

        select_dropdown(self.page, "make_model_list", step1_data["model"])
        self.page.locator("#model_code").fill(step1_data["model_code"])

        self.page.get_by_role("button", name="Continue").click()

        # Wait for step 2 mileage field to confirm step 2 loaded
        self.page.locator("#mileage").wait_for(state="visible")

        # ----- Step 2: Additional Car Details -----
        self.page.locator("#mileage").fill(step2_data["mileage"])
        self.page.locator("#engine").fill(step2_data["engine"])
        select_dropdown(self.page, "color_list", step2_data["color"])
        select_dropdown(self.page, "condition_list", step2_data["condition"])
        select_dropdown(self.page, "car_keys_list", step2_data["keys"])
        select_dropdown(self.page, "original_owner_list", step2_data["original_owner"])

        self.page.set_input_files("#imageInput", IMAGES["mitsubishi"])
        self.page.wait_for_timeout(2000)

        self.page.get_by_role("button", name="Continue").click()

        # Wait for phone field to confirm step 3 loaded
        self.page.locator("#phone").wait_for(state="visible")

        # ----- Step 3: Submit without checking terms checkbox -----
        self.page.get_by_role("button", name="Submit Quote Request").click()

        # Assert terms error message is visible
        assert self.page.locator("#check_terms_policy_err_msg").is_visible(), "❌ Terms error message not visible"
        assert self.page.locator("#check_terms_policy_err_msg").inner_text() == "Please check the Terms and Conditions", "❌ Terms error text incorrect"

        print("❎ Negative Test 3 - Terms Unchecked: Terms and Conditions error correctly shown")


    # ============================================================
    # Positive Test: List on SAT - Full Form Submission
    # ============================================================

    def list_on_sat(self, data):
        self.page.locator("span.user-select-none", has_text="List on SAT").click()
        self.page.get_by_role("link", name="Post My Ad").click()
        self.page.wait_for_load_state("domcontentloaded")

        # Wait for dropdown button to be ready
        self.page.locator("ul#make_list").locator("..").locator("button.satSelectBtn").wait_for(state="visible")

        select_dropdown(self.page, "make_list", data["make"])

        # Wait for model dropdown to be populated after make selection
        self.page.wait_for_function("document.querySelectorAll('#make_model_list li').length > 1")

        select_dropdown(self.page, "make_model_list", data["model"])
        select_dropdown(self.page, "year_list", data["year"])
        select_dropdown(self.page, "fuel_list", data["fuel"])
        select_dropdown(self.page, "steering_list", data["steering"])
        select_dropdown(self.page, "drivetrain_list", data["drivetrain"])
        select_dropdown(self.page, "seats_list", data["seats"])
        select_dropdown(self.page, "countries_list", data["country"])
        self.page.locator("#city").fill(data["city"])
        select_dropdown(self.page, "colors_list", data["color"])
        self.page.locator("#mileage").fill(data["mileage"])
        self.page.locator("#price").fill(data["price"])
        self.page.locator("#engine").fill(data["engine"])
        select_dropdown(self.page, "transmissions_list", data["transmission"])
        self.page.locator("#description").fill(data["description"])

        self.page.set_input_files("#imageInput", IMAGES[data["images"]])
        self.page.wait_for_timeout(2000)

        self.page.locator("#phone").fill(data["phone"])
        self.page.get_by_role("button", name="Submit").click()
        self.page.wait_for_url("**/list-your-vehicle-success")

        assert "list-your-vehicle-success" in self.page.url, "❌ List on SAT: Success page URL not found"
        assert self.page.get_by_text("Your Ad Request Has Been Submitted!").is_visible(), "❌ List on SAT: Success message not visible"

        print(f"✅ List on SAT - {data['make']} {data['model']}: PASS")

        # Navigate back to sell page
        self.page.goto(f"{BASE_URL}/sell", wait_until="domcontentloaded")
        self.page.get_by_role("link", name="Get Price Quote").wait_for(state="visible")


    # ============================================================
    # Positive Test: Auction with SAT - Full Form Submission
    # ============================================================

    def auction_with_sat(self, data):
        self.page.locator("span.user-select-none", has_text="Auction with SAT").click()
        self.page.get_by_role("link", name="Auction My Car").click()
        self.page.wait_for_load_state("domcontentloaded")

        # Wait for dropdown button to be ready
        self.page.locator("ul#make_list").locator("..").locator("button.satSelectBtn").wait_for(state="visible")

        select_dropdown(self.page, "make_list", data["make"])

        # Wait for model dropdown to be populated after make selection
        self.page.wait_for_function("document.querySelectorAll('#make_model_list li').length > 1")

        select_dropdown(self.page, "make_model_list", data["model"])
        self.page.locator("#model_code").fill(data["model_code"])
        select_dropdown(self.page, "year_list", data["year"])
        select_dropdown(self.page, "fuel_list", data["fuel"])
        select_dropdown(self.page, "steering_list", data["steering"])
        select_dropdown(self.page, "drivetrain_list", data["drivetrain"])
        select_dropdown(self.page, "seats_list", data["seats"])
        select_dropdown(self.page, "countries_list", data["country"])
        self.page.locator("#city").fill(data["city"])
        select_dropdown(self.page, "colors_list", data["color"])
        self.page.locator("#mileage").fill(data["mileage"])
        self.page.locator("#price").fill(data["price"])
        self.page.locator("#engine").fill(data["engine"])
        select_dropdown(self.page, "transmissions_list", data["transmission"])
        self.page.locator("#bidding_deadline").fill(data["bidding_deadline"])
        self.page.locator("#description").fill(data["description"])

        self.page.set_input_files("#imageInput", IMAGES["suzuki"])
        self.page.wait_for_timeout(2000)

        self.page.locator("#phone").fill(data["phone"])
        self.page.get_by_role("button", name="Submit").click()
        self.page.wait_for_url("**/auction-form-success")

        assert "auction-form-success" in self.page.url, "❌ Auction with SAT: Success page URL not found"
        assert self.page.get_by_text("Your Ad Request Has Been Submitted!").is_visible(), "❌ Auction with SAT: Success message not visible"

        print("✅ Auction with SAT: PASS")