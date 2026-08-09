# ============================================================
# config.py
# This file holds ALL your settings, credentials, and test data.
# Benefit: If anything changes (like a password or URL),
# you only update it HERE, not inside your test files.
# ============================================================

import os
from dotenv import load_dotenv
from datetime import datetime, timedelta

# --- Base directory (folder where config.py lives) ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Load credentials first, then local frequently-changing test records.
# .env.local is ignored by Git so live stock IDs and URLs are not committed.
load_dotenv(os.path.join(BASE_DIR, ".env"))
load_dotenv(os.path.join(BASE_DIR, ".env.local"), override=True)

# --- Site URL ---
BASE_URL = os.getenv("BASE_URL")

# --- Login Credentials ---
LOGIN_EMAIL = os.getenv("LOGIN_EMAIL")
LOGIN_PASSWORD = os.getenv("LOGIN_PASSWORD")

# --- Frequently changing Buy/Auction records ---
BUY_FLOW_URL = os.getenv("BUY_FLOW_URL")
AUCTION_CALCULATOR_STOCK_ID = os.getenv("AUCTION_CALCULATOR_STOCK_ID")
NON_STOLEN_VEHICLE_STOCK_ID = os.getenv("NON_STOLEN_VEHICLE_STOCK_ID")

# --- Image Paths ---
IMAGES_DIR = os.path.join(BASE_DIR, "assets", "images")

IMAGES = {
    "price_quote": [
        os.path.join(IMAGES_DIR, "Honda Vezel White.jpg"),
    ],
    "auction": [
        os.path.join(IMAGES_DIR, "Suzuki Alto Red.jpeg"),
        os.path.join(IMAGES_DIR, "Suzuki Alto White.jpeg"),
    ],
}

# --- Test Data ---

# -------------------------------------------------------
# Non Stolen Vehicle Test Data
# -------------------------------------------------------
NON_STOLEN_VEHICLE_DATA = {
    "valid_stock_id": NON_STOLEN_VEHICLE_STOCK_ID,
    "invalid_stock_id": "INVALID-ID-12345",
    "full_name": "QA Testing Automation",   
    "email": "qa.testmail007021@gmail.com",
    "phone": "07400000000",
    "card_number_valid": "5555555555554444",
    "card_number_incomplete": "555555555555",
    "expiry": "1234",
    "cvc": "123",
    "zip_code": "54000",
}

# -------------------------------------------------------
# Get Price Quote - Step 1: Basic car details
# -------------------------------------------------------
PRICE_QUOTE_DATA = {
    "year": "2024",
    "make": "Suzuki",
    "model": "ALTO",
    "model_code": "TD20",
}

# -------------------------------------------------------
# Get Price Quote - Step 2: Additional car details
# -------------------------------------------------------
PRICE_QUOTE_STEP2_DATA = {
    "mileage": "15000",
    "engine": "660",
    "color": "Pearl",
    "condition": "Used",
    "keys": "2",
    "original_owner": "Yes",
}

# -------------------------------------------------------
# Get Price Quote - Step 3: Personal information
# -------------------------------------------------------
PRICE_QUOTE_STEP3_DATA = {
    "phone": "+447412000000",
}

# -------------------------------------------------------
# Auction with SAT
# -------------------------------------------------------
AUCTION_DATA = {
    "make": "Suzuki",
    "model": "ALTO",
    "model_code": "SU-TD20",
    "year": "2024",
    "fuel": "Petrol",
    "steering": "RHD",
    "drivetrain": "2WD",
    "seats": "5 Seats",
    "country": "Thailand",
    "city": "Bangkok",
    "color": "Red",
    "mileage": "2500",
    "price": "655000",
    "engine": "1300",
    "transmission": "CVT",
    "bidding_deadline": (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%dT09:15"),
    "description": "Everything is in genuine condition. Condition is as good as a brand-new car.",
    "phone": "+447412000000",
}

# -------------------------------------------------------
# Shipping Schedule - Test Data (Multiple Scenarios)
# -------------------------------------------------------
SHIPPING_SCHEDULE_SCENARIOS = [
    {
        "name": "Valid filters - shows results",
        "departure_port": "Yokohama",
        "region": "Africa",
        "arrival_port": "Durban",
        "ship_name": "Orion Leader",
        "expected": "results"
    },
    {
        "name": "Invalid filters - shows no results",
        "departure_port": "Moji",
        "region": "Chile",
        "arrival_port": "Iquique",
        "ship_name": "Orion Leader",
        "expected": "no_results"
    },
]

# Keep original single data for backward compatibility
SHIPPING_SCHEDULE_DATA = SHIPPING_SCHEDULE_SCENARIOS[0]
