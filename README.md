# SAT Japan - Test Automation Framework
![Python](https://img.shields.io/badge/Python-3.11-blue)
![Playwright](https://img.shields.io/badge/Playwright-Test%20Automation-green)
![Pytest](https://img.shields.io/badge/Pytest-Test%20Runner-orange)
![License](https://img.shields.io/badge/License-MIT-lightgrey)

An end-to-end test automation framework for the [SAT Japan](https://development.satjapan.info) vehicle selling platform, built with Python, Playwright, and pytest.

---

## About the Project

This framework automates the core workflows on the SAT Japan platform, including:

**Sell My Car Module:**
- Getting a price quote for a vehicle
- Listing a vehicle for sale
- Auctioning a vehicle

**Car Services Module:**
- Auction Service - Bid on vehicles
- Shipping Schedule - Filter and view shipping schedules

It covers both positive and negative test scenarios, following the Page Object Model (POM) design pattern for clean and maintainable test code.

---

## Tech Stack

| Tool | Purpose |
|------|---------|
| Python 3.11+ | Programming language |
| Playwright | Browser automation |
| pytest | Test runner |
| pytest-html | HTML test reports |
| python-dotenv | Secure credentials management |

---

## Project Structure
```
SAT_Automation/
├── assets/
│ └── images/ # Test images for form uploads
│
├── pages/
│ ├── auth/
│ │ └── login_page.py # Login page actions
│ │
│ ├── car_services/
│ │ ├── car_services_page.py # Car Services hover menu navigation
│ │ ├── auction_service_page.py # Auction Service page actions
│ │ └── shipping_schedule_page.py # Shipping Schedule page actions
│ │
│ └── sell_my_car/
│ └── sell_page.py # Sell My Car page actions
│
├── reports/
│ ├── report.html # Generated HTML test report
│ └── screenshots/ # Auto-captured screenshots on test failure
│
├── tests/
│ ├── sell_my_car/
│ │ ├── init.py
│ │ ├── test_sell.py # Positive test cases (8 tests)
│ │ └── test_sell_negative.py # Negative test cases (3 tests)
│ │
│ └── car_services/
│ ├── init.py
│ ├── test_auction_service.py # Auction Service test cases (4 tests)
│ └── test_shipping_schedule.py # Shipping Schedule test cases (5 tests)
│
├── .env
├── .gitignore
├── config.py
├── conftest.py
├── pytest.ini
└── README.md
```

---

## Setup Instructions

### 1. Clone the repository
```
git clone https://github.com/your-username/SAT_Automation.git
cd SAT_Automation
```

### 2. Create and activate virtual environment
```
python -m venv venv

# Windows
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate
```

### 3. Install dependencies
```
pip install playwright pytest pytest-html python-dotenv
playwright install
```

### 4. Create .env file

Create a .env file inside the SAT_Automation/ folder:
```
BASE_URL=https://development.satjapan.info
LOGIN_EMAIL=your_email@example.com
LOGIN_PASSWORD=your_password
```

### 5. Add test images

Place your test images inside SAT_Automation/assets/images/. Required images:
- aqua1.jpeg, aqua2.jpeg, aqua3.jpeg
- suzuki1.jpeg, suzuki2.jpeg
- mitsubishi.PNG
- Nissan1.jpg, Nissan2.jpg, Nissan3.jpg, Nissan4.jpg, Nissan5.jpg
- honda1.jpg, honda2.jpg, honda3.jpg

---

## How to Run Tests

Run all tests:
```
pytest
```

Run only positive tests:
```
pytest SAT_Automation/tests/test_sell.py
```

Run only negative tests:
```
pytest SAT_Automation/tests/test_sell_negative.py
```

Run a single specific test:
```
pytest SAT_Automation/tests/test_sell.py::test_get_price_quote
```

---

## Test Cases Summary

### Sell My Car Module (11 tests)

| Test File | Test Count | Description |
|-----------|------------|-------------|
| test_sell.py | 8 | Positive tests (Price Quote, List on SAT with 3 params, Auction) |
| test_sell_negative.py | 3 | Negative tests (empty fields, partial validation, terms unchecked) |

### Car Services Module (9 tests)

| Test File | Test Count | Description |
|-----------|------------|-------------|
| test_auction_service.py | 4 | Auction Service - vehicle search and bid submission |
| test_shipping_schedule.py | 5 | Shipping Schedule - page verification, dropdown filters, date filters |

### Total Tests: 20

---

## Key Features

- Page Object Model (POM) - Each page has its own class
- Secure credentials - Login details stored in .env file, never hardcoded
- Session-based login - Logs in once and reuses session across all tests
- Auto screenshots - Captures screenshots on any test failure
- Parameterized tests - List on SAT runs with 3 different data sets; Shipping Schedule runs with valid/invalid scenarios
- Positive and negative tests - Covers both happy path and validation scenarios
- Proper waits - No hardcoded sleeps; uses Playwright's built-in wait methods
- Select2 dropdown handling - Custom handling for Select2 dropdowns
- Datepicker handling - Uses `:visible` selector for dynamic calendars

---

## Reports

After running tests, open the HTML report:
```
reports/report.html
```

The report includes pass/fail status, test duration, and screenshots for any failed test.

---

## Future Plans

- Add negative test cases for List on SAT and Auction with SAT
- Expand to other site modules (Buy, Search, User Profile)
- Add pytest markers for smoke and regression test groups
- Integrate with GitHub Actions for CI/CD
- Add headless mode for faster execution in CI/CD pipelines
- Generate Allure reports for richer test reporting

---

## Notes

- Tests run in a real Chromium browser so you can watch them execute
- The .env file is excluded from GitHub via .gitignore to keep credentials safe
- Images used for testing are excluded from GitHub - add your own to assets/images/
