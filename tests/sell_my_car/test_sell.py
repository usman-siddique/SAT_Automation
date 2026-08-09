import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from config import AUCTION_DATA
from config import PRICE_QUOTE_DATA, PRICE_QUOTE_STEP2_DATA, PRICE_QUOTE_STEP3_DATA
from data.list_on_sat_data import LIST_ON_SAT_PARAMS
from pages.sell_my_car.sell_page import SellPage


def setup_sell_page(page):
    sell_page = SellPage(page)
    sell_page.go_to_sell_page()
    return sell_page


def listing_id(list_data):
    """Create a readable ID for every independent listing test item."""
    return "-".join(
        str(list_data.get(field, field)).strip().replace(" ", "-").lower()
        for field in ("make", "model", "year")
    )


class TestSellMyCar:
    """Sell My Car flows that pytest can execute and rerun independently."""

    def test_get_price_quote(self, require_state_changing_tests, page):
        print("\nStarting Get Price Quote...")
        sell_page = setup_sell_page(page)
        sell_page.get_price_quote(
            PRICE_QUOTE_DATA,
            PRICE_QUOTE_STEP2_DATA,
            PRICE_QUOTE_STEP3_DATA,
        )

    @pytest.mark.parametrize("list_data", LIST_ON_SAT_PARAMS, ids=listing_id)
    def test_list_on_sat(self, require_state_changing_tests, page, list_data):
        print(
            f"\nStarting List on SAT - "
            f"{list_data['make']} {list_data['model']}..."
        )
        sell_page = setup_sell_page(page)
        sell_page.list_on_sat(list_data)

    def test_auction_with_sat(self, require_state_changing_tests, page):
        print("\nStarting Auction with SAT...")
        sell_page = setup_sell_page(page)
        sell_page.auction_with_sat(AUCTION_DATA)
