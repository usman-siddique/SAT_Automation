from decimal import Decimal

import allure

from config import (
    AUCTION_CALCULATOR_COUNTRY,
    AUCTION_CALCULATOR_PORT,
    AUCTION_CALCULATOR_STOCK_ID,
)
from pages.car_services.auction_service_page import AuctionServicePage
from pages.car_services.car_services_page import CarServicesPage


def open_auction_service(page):
    CarServicesPage(page).go_to_auction_service()
    return AuctionServicePage(page)


def test_auction_service_overview_actions_and_faqs(page):
    auction = open_auction_service(page)

    with allure.step("Verify Auction Service Overview content and targets"):
        overview = auction.get_overview()
        assert overview["heading"] == "Auction Service Overview"
        assert "competitive bidding process" in overview["description"]
        assert overview["links"]["start_bidding"].endswith(
            "/used-cars/auction_cars"
        )
        assert overview["links"]["calculator"].endswith(
            "/auction-calculator"
        )
        assert overview["links"]["sheet_guide"].endswith(
            "/pdfs/Auction_Sheet_Guide.pdf"
        )
        assert overview["links"]["house_map"].endswith(
            "/pdfs/auctions_map_house.pdf"
        )

    with allure.step("Download and validate both Auction Overview PDFs"):
        for filename in (
            "Auction_Sheet_Guide.pdf",
            "auctions_map_house.pdf",
        ):
            document = auction.download_overview_pdf(filename)
            assert document["filename"].lower() == filename.lower()
            assert document["failure"] is None
            assert document["size"] > 1_000
            assert document["header"] == b"%PDF-"

    with allure.step("Verify Auction FAQ tabs"):
        assert auction.get_faq_tabs() == [
            {
                "label": "Bidding and Auction",
                "target": "#v_pills_bidding",
                "selected": "true",
            },
            {
                "label": "Costs and Shipping",
                "target": "#v_pills_shipping",
                "selected": "false",
            },
        ]

    with allure.step("Expand and verify every Bidding and Auction FAQ"):
        bidding = auction.select_faq_tab_and_expand_all(
            "Bidding and Auction"
        )
        assert bidding["selected"] == "true"
        assert bidding["questions"] == list(
            AuctionServicePage.BIDDING_QUESTIONS
        )
        assert all(len(answer) >= 30 for answer in bidding["answers"])

    with allure.step("Switch tabs and verify every Costs and Shipping FAQ"):
        shipping = auction.select_faq_tab_and_expand_all(
            "Costs and Shipping"
        )
        assert shipping["selected"] == "true"
        assert shipping["questions"] == list(
            AuctionServicePage.COST_AND_SHIPPING_QUESTIONS
        )
        assert all(len(answer) >= 30 for answer in shipping["answers"])

    with allure.step("Verify Start Bidding destination"):
        destination = auction.open_start_bidding()
        assert destination == {
            "path": "/used-cars/auction_cars",
            "auction_tab_active": True,
        }

    with allure.step("Return and verify Auction Cost Calculator destination"):
        auction.return_to_auction_service()
        assert auction.open_cost_calculator() == {
            "path": "/auction-calculator",
            "heading": "Auction Cost Calculator",
        }


def test_auction_cost_calculator_auto_fetch_and_estimate(page):
    auction = open_auction_service(page)
    auction.open_cost_calculator()

    with allure.step("Load the configured auction stock and auto-fetch data"):
        data = auction.load_stock_data(
            AUCTION_CALCULATOR_STOCK_ID,
            AUCTION_CALCULATOR_COUNTRY,
            AUCTION_CALCULATOR_PORT,
        )
        assert data["stock_id"].lower() == (
            AUCTION_CALCULATOR_STOCK_ID.strip().lower()
        )
        assert data["car_id"]
        assert data["bid_input"] > 0
        assert data["m3"] > 0
        assert data["country"] == AUCTION_CALCULATOR_COUNTRY
        assert data["port"] == AUCTION_CALCULATOR_PORT

    with allure.step("Verify the fetched bid and deposit calculation"):
        assert data["bidding_amount"] == data["bid_input"]
        assert Decimal("0") < data["deposit"] <= data["bid_input"]

    with allure.step("Verify the complete cost breakdown and total"):
        assert data["inspection"] >= 0
        assert data["insurance"] >= 0
        assert data["shipping"] >= 0
        assert len(data["displayed_totals"]) == 2
        if data["agent_fee"] is None:
            assert data["agent_fee_text"].lower() == "ask"
            assert data["total"] is None
            assert data["displayed_totals"] == [None, None]
        else:
            expected_total = (
                data["bidding_amount"]
                + data["agent_fee"]
                + data["inspection"]
                + data["insurance"]
                + data["shipping"]
            )
            assert (
                abs(data["total"] - expected_total) <= Decimal("0.01")
            )
            assert all(
                abs(total - data["total"]) <= Decimal("0.01")
                for total in data["displayed_totals"]
            )

    with allure.step("Open and verify the generated auction estimate"):
        estimate = auction.open_estimate(data)
        assert estimate == {
            "path": "/download-estimate",
            "heading": (
                f"Auction Cost Calculator for {data['country']}"
            ),
            "stock_id_visible": True,
            "cost_breakdown_visible": True,
            "amounts_visible": True,
            "pdf_action_working": True,
        }


def test_auction_calculator_unknown_stock_and_missing_destinations(
    page_no_login,
):
    auction = open_auction_service(page_no_login)
    auction.open_cost_calculator()

    with allure.step("Reject an unknown stock without generating an estimate"):
        invalid = auction.verify_unknown_stock_blocks_estimate(
            "SAT-72073083"
        )
        assert invalid == {
            "message": "Auction car not found",
            "estimate_generated": False,
        }

    with allure.step("Reject missing country and port estimate states"):
        page_no_login.reload(wait_until="domcontentloaded")
        page_no_login.get_by_role(
            "heading", name="Auction Cost Calculator", exact=True
        ).wait_for(state="visible")
        missing = auction.verify_missing_destinations_block_estimate(
            AUCTION_CALCULATOR_STOCK_ID,
            AUCTION_CALCULATOR_COUNTRY,
            AUCTION_CALCULATOR_PORT,
        )
        assert missing == {
            "missing_country": False,
            "missing_port": False,
        }


def test_auction_calculator_bid_boundaries_block_invalid_estimates(
    page_no_login,
):
    auction = open_auction_service(page_no_login)
    auction.open_cost_calculator()

    with allure.step("Reject empty, zero, and negative bid estimates"):
        result = auction.verify_bid_boundaries(
            AUCTION_CALCULATOR_STOCK_ID,
            AUCTION_CALCULATOR_COUNTRY,
            AUCTION_CALCULATOR_PORT,
        )
        failures = {
            state: details
            for state, details in result["invalid"].items()
            if details["estimate_generated"]
        }
        assert not failures, (
            "Invalid bid states generated auction estimates: "
            f"{failures}"
        )

    with allure.step("Accept the minimum positive bid boundary"):
        assert result["minimum"]["bid_amount"] == Decimal("1")
        assert result["minimum"]["total"] is not None
        assert result["minimum"]["total"] > Decimal("1")
        assert result["minimum"]["estimate_generated"] is True
