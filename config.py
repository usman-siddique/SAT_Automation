# ============================================================
# config.py
# This file holds ALL your settings, credentials, and test data.
# Benefit: If anything changes (like a password or URL),
# you only update it HERE, not inside your test files.
# ============================================================

import os
from dotenv import load_dotenv
from datetime import datetime, timedelta

from data.payment_cards import ACTIVE_TEST_CARD, TEST_PAYMENT_CARDS
from data.stock_ids import STOCK_IDS

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
REJECTED_DEALER_USER_EMAIL = os.getenv(
    "REJECTED_DEALER_USER_EMAIL", LOGIN_EMAIL
)
REJECTED_DEALER_USER_PASSWORD = os.getenv(
    "REJECTED_DEALER_USER_PASSWORD", LOGIN_PASSWORD
)
DEALER_LOGIN_EMAIL = os.getenv("DEALER_LOGIN_EMAIL")
DEALER_LOGIN_PASSWORD = os.getenv("DEALER_LOGIN_PASSWORD")
ELIGIBLE_DEALER_USER_EMAIL = os.getenv("ELIGIBLE_DEALER_USER_EMAIL")
ELIGIBLE_DEALER_USER_PASSWORD = os.getenv("ELIGIBLE_DEALER_USER_PASSWORD")
DEALER_TEST_PASSWORD = os.getenv("DEALER_TEST_PASSWORD")
PAYPAL_SANDBOX_EMAIL = os.getenv("PAYPAL_SANDBOX_EMAIL")
PAYPAL_SANDBOX_PASSWORD = os.getenv("PAYPAL_SANDBOX_PASSWORD")
TRACK_ORDER_ID = os.getenv("TRACK_ORDER_ID", "804655248")
TRACK_ORDER_EMAIL = os.getenv(
    "TRACK_ORDER_EMAIL", "dealerflow2@gmail.com"
)
TRACK_ORDER_MISMATCH_EMAIL = os.getenv(
    "TRACK_ORDER_MISMATCH_EMAIL", "usmanqaengineer@gmail.com"
)
TRACK_ORDER_UNKNOWN_ID = os.getenv(
    "TRACK_ORDER_UNKNOWN_ID", "999999999999999"
)

# --- Inquiry Form test data ---
INQUIRY_FORM_DATA = {
    "name": os.getenv("INQUIRY_NAME", "SAT QA Automation"),
    "email": os.getenv("INQUIRY_EMAIL", LOGIN_EMAIL),
    "phone": os.getenv("INQUIRY_PHONE", "+923008090100"),
    "country": os.getenv("INQUIRY_COUNTRY", "Pakistan"),
    "city": os.getenv("INQUIRY_CITY", "Karachi"),
    "question": os.getenv(
        "INQUIRY_QUESTION",
        "Automated QA test inquiry from SAT Automation. Please ignore.",
    ),
}

VEHICLE_INFORMATION_REQUEST_DATA = {
    "make": "Toyota",
    "model": "AQUA",
    "body_type": "Hatchback",
    "steering": "RHD",
    "country": "Pakistan",
    "email": INQUIRY_FORM_DATA["email"],
    "min_year": "2020",
    "max_year": "2022",
    "min_price": "3,000",
    "max_price": "10,000",
    "min_mileage": "10,000",
    "max_mileage": "100,000",
    "question": (
        "Automated vehicle information request from SAT Automation. "
        "Please ignore."
    ),
}

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
USED_CAR_PAYPAL_PATH = os.getenv(
    "USED_CAR_PAYPAL_PATH",
    "/used-cars/mk_suzuki?sort_by=new_arrival&per_page=25&page=1&unreserved=1",
)
USED_CAR_RESERVATION_PATH = os.getenv(
    "USED_CAR_RESERVATION_PATH",
    "/used-cars?unreserved=1",
)

USED_CAR_PAYGENT_URL = build_site_url(USED_CAR_PAYGENT_PATH)
USED_CAR_BANK_URL = build_site_url(USED_CAR_BANK_PATH)
USED_CAR_PAYPAL_URL = build_site_url(USED_CAR_PAYPAL_PATH)
USED_CAR_RESERVATION_URL = build_site_url(USED_CAR_RESERVATION_PATH)
USED_CAR_PAYPAL_COUNTRY = "United Kingdom"
USED_CAR_PAYPAL_PORT = "Bristol"
USED_CAR_PAYPAL_SHIPPING_TYPE = "roro"

# --- Stock IDs (all editable values live in data/stock_ids.py) ---
AUCTION_CALCULATOR_STOCK_ID = STOCK_IDS["auction_calculator"]
AUCTION_CALCULATOR_COUNTRY = os.getenv(
    "AUCTION_CALCULATOR_COUNTRY", "Pakistan"
)
AUCTION_CALCULATOR_PORT = os.getenv("AUCTION_CALCULATOR_PORT", "Karachi")
NON_STOLEN_VEHICLE_STOCK_ID = STOCK_IDS["non_stolen_vehicle"]

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

SELLER_REGISTRATION_DOCUMENT = os.path.join(
    IMAGES_DIR,
    "Honda Vezel White.jpg",
)

SELLER_REGISTRATION_DATA = {
    "company_name": "SAT QA Motors",
    "country": "Pakistan",
    "registration_number": "SAT-QA-REG-001",
    "website": "https://example.com",
    "contact_name": "SAT QA Seller",
    "email": "seller.automation@gmail.com",
    "phone_number": "3001234567",
    "seller_type": "individual",
    "monthly_availability": "6-10",
    "vehicle_locations": ["Pakistan", "Japan"],
    "vehicle_types": ["cars", "suvs"],
}

# --- Test Data ---

# -------------------------------------------------------
# Non Stolen Vehicle Test Data
# -------------------------------------------------------
NON_STOLEN_VEHICLE_DATA = {
    "valid_stock_id": NON_STOLEN_VEHICLE_STOCK_ID,
    "invalid_stock_id": STOCK_IDS["invalid"],
    "full_name": "QA Testing Automation",
    "email": "qa.testmail007021@gmail.com",
    "phone": "07400000000",
    "phone_country": "gb",
    "payment_card": TEST_PAYMENT_CARDS[ACTIVE_TEST_CARD],
}

ACTIVE_PAYMENT_CARD = TEST_PAYMENT_CARDS[ACTIVE_TEST_CARD]

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
