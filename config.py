# ============================================================
# config.py
# This file holds ALL your settings, credentials, and test data.
# Benefit: If anything changes (like a password or URL),
# you only update it HERE, not inside your test files.
# ============================================================

import os
from dotenv import load_dotenv
from datetime import datetime, timedelta

# Load values from .env file into environment variables
load_dotenv()

# --- Base directory (folder where config.py lives) ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# --- Site URL ---
BASE_URL = os.getenv("BASE_URL")

# --- Login Credentials ---
LOGIN_EMAIL = os.getenv("LOGIN_EMAIL")
LOGIN_PASSWORD = os.getenv("LOGIN_PASSWORD")

# --- Image Paths ---
IMAGES_DIR = os.path.join(BASE_DIR, "assets", "images")

IMAGES = {
    "aqua": [
        os.path.join(IMAGES_DIR, "aqua1.jpeg"),
        os.path.join(IMAGES_DIR, "aqua2.jpeg"),
        os.path.join(IMAGES_DIR, "aqua3.jpeg"),
    ],
    "suzuki": [
        os.path.join(IMAGES_DIR, "suzuki1.jpeg"),
        os.path.join(IMAGES_DIR, "suzuki2.jpeg"),
    ],
    "mitsubishi": [
        os.path.join(IMAGES_DIR, "mitsubishi.PNG"),
    ],
    "nissan": [
        os.path.join(IMAGES_DIR, "Nissan1.jpg"),
        os.path.join(IMAGES_DIR, "Nissan2.jpg"),
        os.path.join(IMAGES_DIR, "Nissan3.jpg"),
        os.path.join(IMAGES_DIR, "Nissan4.jpg"),
        os.path.join(IMAGES_DIR, "Nissan5.jpg"),
    ],
    "honda": [
        os.path.join(IMAGES_DIR, "honda1.jpg"),
        os.path.join(IMAGES_DIR, "honda2.jpg"),
        os.path.join(IMAGES_DIR, "honda3.jpg"),
    ],
}

# --- Test Data ---

# -------------------------------------------------------
# Non Stolen Vehicle Test Data
# -------------------------------------------------------
NON_STOLEN_VEHICLE_DATA = {
    "valid_stock_id": "SAT-67528721",
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
# List on SAT - Parametrized data sets
# -------------------------------------------------------
LIST_ON_SAT_PARAMS = [
    {
        "make": "Toyota",
        "model": "AQUA",
        "year": "2024",
        "fuel": "Petrol",
        "steering": "RHD",
        "drivetrain": "2WD",
        "seats": "5 Seats",
        "country": "United Kingdom",
        "city": "Bristol",
        "color": "Blue",
        "mileage": "5500",
        "price": "5550000",
        "engine": "1300",
        "transmission": "CVT",
        "description": "Everything is in genuine condition. Condition is as good as a brand-new car.",
        "phone": "+447412000000",
        "images": "aqua",
    },
    {
        "make": "Nissan",
        "model": "FAIRLADY Z",
        "year": "2022",
        "fuel": "Diesel",
        "steering": "RHD",
        "drivetrain": "2WD",
        "seats": "5 Seats",
        "country": "Thailand",
        "city": "Bangkok",
        "color": "Black",
        "mileage": "12000",
        "price": "3500000",
        "engine": "2000",
        "transmission": "CVT",
        "description": "Low mileage vehicle with full service history. Well maintained and in excellent condition.",
        "phone": "+66812345678",
        "images": "nissan",
    },
    {
        "make": "Honda",
        "model": "FIT",
        "year": "2023",
        "fuel": "Petrol",
        "steering": "RHD",
        "drivetrain": "2WD",
        "seats": "5 Seats",
        "country": "Australia",
        "city": "Melbourne",
        "color": "White",
        "mileage": "8000",
        "price": "2800000",
        "engine": "1500",
        "transmission": "CVT",
        "description": "Single owner vehicle. All original parts. Never been in an accident.",
        "phone": "+61412345678",
        "images": "honda",
    },
]

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