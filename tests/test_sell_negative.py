# ============================================================
# tests/test_sell_negative.py
#
# Negative test cases - validating form error messages
# HOW TO RUN:
#   pytest SAT_Automation/tests/test_sell_negative.py -v -s
# ============================================================

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from config import PRICE_QUOTE_DATA, PRICE_QUOTE_STEP2_DATA, PRICE_QUOTE_STEP3_DATA
from pages.sell_page import SellPage


def setup_sell_page(page):
    sell_page = SellPage(page)
    sell_page.go_to_sell_page()
    return sell_page


# ============================================================
# Negative Test 1: Get Price Quote - Step 1 All Fields Empty
# ============================================================

def test_get_price_quote_empty_fields(page):
    print("\n📝 Starting Get Price Quote Empty Fields Validation...")
    sell_page = setup_sell_page(page)
    sell_page.get_price_quote_validation()


# ============================================================
# Negative Test 2: Get Price Quote - Step 1 Partial Validation
# Only Year filled, Make and Model left empty
# ============================================================

def test_get_price_quote_partial_validation(page):
    print("\n📝 Starting Get Price Quote Partial Validation...")
    sell_page = setup_sell_page(page)
    sell_page.get_price_quote_partial_validation(PRICE_QUOTE_DATA)


# ============================================================
# Negative Test 3: Get Price Quote - Step 3 Terms Checkbox Unchecked
# ============================================================

def test_get_price_quote_terms_validation(page):
    print("\n📝 Starting Get Price Quote Terms Validation...")
    sell_page = setup_sell_page(page)
    sell_page.get_price_quote_terms_validation(PRICE_QUOTE_DATA, PRICE_QUOTE_STEP2_DATA, PRICE_QUOTE_STEP3_DATA)