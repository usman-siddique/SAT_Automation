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

# Preserve an environment selected by run_tests.bat before loading .env.
RUNTIME_BASE_URL = os.getenv("BASE_URL")

# Load the project's single private environment file. It is ignored by Git.
load_dotenv(os.path.join(BASE_DIR, ".env"))

# --- Site URL ---
# run_tests.bat sets BASE_URL for the selected environment. Direct pytest runs
# fall back to the value in .env.
BASE_URL = (RUNTIME_BASE_URL or os.getenv("BASE_URL") or "").rstrip("/")

if not BASE_URL:
    raise RuntimeError(
        "BASE_URL is missing. Select an environment in run_tests.bat or set "
        "BASE_URL in .env."
    )


def build_site_url(path: str) -> str:
    """Build a URL on the currently selected test environment."""
    return f"{BASE_URL}/{path.lstrip('/')}"

# --- Login Credentials ---
LOGIN_EMAIL = os.getenv("LOGIN_EMAIL")
LOGIN_PASSWORD = os.getenv("LOGIN_PASSWORD")

# --- Buy flow inventory paths ---
# Keep the environment domain separate from stable inventory paths so the same
# tests can run against Sprint or Development without duplicating URLs.
USED_CAR_PAYGENT_PATH = os.getenv(
    "USED_CAR_PAYGENT_PATH",
    "/used-cars/mk_volkswagen?sort_by=new_arrival&per_page=25&page=1&unreserved=1",
)
USED_CAR_BANK_PATH = os.getenv(
    "USED_CAR_BANK_PATH",
    "/used-cars/mk_daihatsu?sort_by=new_arrival&per_page=25&page=1&unreserved=1",
)

USED_CAR_PAYGENT_URL = build_site_url(USED_CAR_PAYGENT_PATH)
USED_CAR_BANK_URL = build_site_url(USED_CAR_BANK_PATH)

# --- Frequently changing Auction/Service records ---
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
