# ============================================================
# pages/car_services/auction_service_page.py
# Contains the AuctionServicePage class.
# Handles all actions on the Auction Service landing page.
# ============================================================

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from playwright.sync_api import TimeoutError as PlaywrightTimeoutError

# ============================================================
# Page Class: Auction Service Page
# ============================================================

class AuctionServicePage:
    def __init__(self, page, context=None):
        self.page = page
        self.context = context


    # ============================================================
    # Helper: Select Destination Country or Port dropdown
    # ============================================================

    def select_destination_dropdown(self, block_id, li_class, value):
        block = self.page.locator(f"#{block_id}")
        
        # Retry up to 2 times if dropdown fails
        for attempt in range(2):
            try:
                block.locator("button.satSelectBtn").click()
                item = block.locator(f"li.{li_class}", has_text=value)
                item.wait_for(state="visible", timeout=5000)
                item.scroll_into_view_if_needed()
                item.click()
                return
            except:
                if attempt == 1:
                    raise
                self.page.wait_for_timeout(1000)


    # ============================================================
    # Action: Click Start Bidding, validate redirect to auction listing
    # ============================================================

    def click_start_bidding(self):
        self.page.get_by_role("link", name="Start Bidding").click()
        self.page.wait_for_url("**/used-cars/auction_cars**")

        self.page.locator("#nav-auction-tab.active").wait_for(state="visible")

        print("✅ Start Bidding redirect to Auction listing: PASS")


    # ============================================================
    # Action: Click Auction Cost Calculator, validate redirect
    # ============================================================

    def click_auction_cost_calculator(self):
        self.page.get_by_role("link", name="Auction Cost Calculator").click()
        self.page.wait_for_url("**/auction-calculator")

        self.page.get_by_role("heading", name="Auction Cost Calculator").wait_for(state="visible")

        print("✅ Auction Cost Calculator redirect: PASS")


    # ============================================================
    # Action: Fill Auction Cost Calculator form and validate
    # cost breakdown fields, then validate Download Estimate
    # opens new tab with PDF invoice
    # ============================================================

    def fill_auction_cost_calculator(self, stock_id, bid_amount, country, port):
        if not stock_id:
            raise AssertionError(
                "AUCTION_CALCULATOR_STOCK_ID is missing. "
                "Update it in .env before running."
            )

        # Fill Stock ID and wait for either of the two supported API outcomes:
        # vehicle data is returned, or the stock is no longer available.
        normalized_stock_id = stock_id.strip().lower()
        self.page.locator("#stock_id").fill(normalized_stock_id)
        try:
            result = self.page.wait_for_function(
                """
                () => {
                    const m3 = document.querySelector('#m3');
                    if (m3 && m3.value.trim() !== '') {
                        return 'available';
                    }

                    const notFoundMessage = Array.from(
                        document.querySelectorAll('body *')
                    ).find((element) => {
                        const text = (element.textContent || '').trim();
                        if (text !== 'Auction car not found') {
                            return false;
                        }

                        const style = window.getComputedStyle(element);
                        return style.display !== 'none'
                            && style.visibility !== 'hidden'
                            && style.opacity !== '0';
                    });

                    return notFoundMessage ? 'not_found' : false;
                }
                """,
                timeout=15000,
            )
            outcome = result.json_value()
        except PlaywrightTimeoutError as error:
            raise AssertionError(
                f"Auction stock {stock_id} returned neither vehicle data nor "
                "the expected 'Auction car not found' validation within 15 seconds."
            ) from error

        if outcome == "not_found":
            not_found_message = self.page.get_by_text(
                "Auction car not found",
                exact=True,
            ).first
            assert not_found_message.is_visible(), (
                "Expected 'Auction car not found' validation is not visible"
            )
            print(
                "✅ Unavailable auction stock returned the expected "
                "'Auction car not found' validation: PASS"
            )
            return "not_found"

        print("✅ Stock ID entered, M3 auto-fetched: PASS")

        # Select destination country and port
        self.select_destination_dropdown("destination_country_block", "data-li-destination_country", country)
        self.select_destination_dropdown("destination_port_block", "data-li-destination_port", port)

        print("✅ Destination Country and Port selected: PASS")

        # Clear auto-filled bid amount and enter manually
        self.page.locator("#bidInput").clear()
        self.page.locator("#bidInput").fill(bid_amount)

        # Validate cost breakdown fields are populated
        assert self.page.locator("#bidAmount").is_visible(), "❌ Bid Amount not visible"
        assert self.page.locator("#agent_fee_dtl").is_visible(), "❌ Agent Fee not visible"
        assert self.page.locator("#inspection_fee_dtl").is_visible(), "❌ Inspection Fee not visible"
        assert self.page.locator("#insurance_fee_dtl").is_visible(), "❌ Insurance Fee not visible"
        assert self.page.locator("#shipping_fee_dtl").is_visible(), "❌ Shipping Fee not visible"
        assert self.page.locator("span.total_price_of_bid").is_visible(), "❌ Total Price not visible"

        print("✅ Cost breakdown fields populated: PASS")

        # Click Download Estimate and handle new tab
        with self.context.expect_page() as new_page_info:
            self.page.locator("#downloadEstimate").click()

        new_tab = new_page_info.value
        new_tab.wait_for_url("**/download-estimate")

        # Validate heading contains country name
        new_tab.get_by_role("heading", name=f"Auction Cost Calculator for {country}").wait_for(state="visible")

        # Validate Download as PDF button is visible
        new_tab.locator("button.sat-btn.primary").wait_for(state="visible")

        # Validate entered bid amount is shown in invoice
        formatted_amount = f"${int(bid_amount):,}"
        new_tab.locator("span.value", has_text=formatted_amount).wait_for(state="visible")

        print("✅ Download Estimate opened with PDF invoice: PASS")

        # Close new tab
        new_tab.close()
        return "available"
