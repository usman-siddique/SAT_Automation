# ============================================================
# tests/test_sell.py
#
# HOW TO RUN:
#   pytest SAT_Automation/tests/test_sell.py -v --html=SAT_Automation/reports/report.html
# ============================================================

import pytest
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from config import PRICE_QUOTE_DATA, PRICE_QUOTE_STEP2_DATA, PRICE_QUOTE_STEP3_DATA
from config import LIST_ON_SAT_PARAMS, AUCTION_DATA
from pages.sell_page import SellPage


def setup_sell_page(page):
    sell_page = SellPage(page)
    sell_page.go_to_sell_page()
    return sell_page


# ============================================================
# Test 1: Get Price Quote - all 3 steps
# ============================================================

def test_get_price_quote(page):
    print("\n📝 Starting Get Price Quote...")
    sell_page = setup_sell_page(page)
    sell_page.get_price_quote(PRICE_QUOTE_DATA, PRICE_QUOTE_STEP2_DATA, PRICE_QUOTE_STEP3_DATA)


# ============================================================
# Test 2: List on SAT
# ============================================================

@pytest.mark.parametrize("list_data", LIST_ON_SAT_PARAMS)
def test_list_on_sat(page, list_data):
    print(f"\n📝 Starting List on SAT - {list_data['make']} {list_data['model']}...")
    sell_page = setup_sell_page(page)
    sell_page.list_on_sat(list_data)


# ============================================================
# Test 3: Auction with SAT
# ============================================================

def test_auction_with_sat(page):
    print("\n📝 Starting Auction with SAT...")
    sell_page = setup_sell_page(page)
    sell_page.auction_with_sat(AUCTION_DATA)