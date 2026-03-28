# ============================================================
# tests/car_services/test_auction_service.py
#
# HOW TO RUN:
#   pytest tests/car_services/test_auction_service.py -v -s
# ============================================================

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from pages.car_services.car_services_page import CarServicesPage
from pages.car_services.auction_service_page import AuctionServicePage


# ============================================================
# Test 1: Verify navigation to Auction Service page
# ============================================================

def test_navigate_to_auction_service(page):
    print("\n📝 Starting Auction Service Navigation...")
    CarServicesPage(page).go_to_auction_service()


# ============================================================
# Test 2: Verify Start Bidding redirects to auction listing
# ============================================================

def test_start_bidding_redirect(page):
    print("\n📝 Starting Start Bidding Redirect...")
    CarServicesPage(page).go_to_auction_service()
    AuctionServicePage(page).click_start_bidding()


# ============================================================
# Test 3: Verify Auction Cost Calculator redirect
# ============================================================

def test_auction_cost_calculator_redirect(page):
    print("\n📝 Starting Auction Cost Calculator Redirect...")
    CarServicesPage(page).go_to_auction_service()
    AuctionServicePage(page).click_auction_cost_calculator()


# ============================================================
# Test 4: Fill Auction Cost Calculator form and validate
# cost breakdown and Download Estimate new tab
# ============================================================

def test_auction_cost_calculator_form(page, context):
    print("\n📝 Starting Auction Cost Calculator Form...")
    CarServicesPage(page).go_to_auction_service()
    AuctionServicePage(page, context).click_auction_cost_calculator()
    AuctionServicePage(page, context).fill_auction_cost_calculator(
        stock_id="sat-85775462",
        bid_amount="1500",
        country="Australia",
        port="Melbourne"
    )