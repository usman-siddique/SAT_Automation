# SAT Japan - Test Automation Framework

![Python](https://img.shields.io/badge/Python-3.11-blue)
![Playwright](https://img.shields.io/badge/Playwright-Test%20Automation-green)
![Pytest](https://img.shields.io/badge/Pytest-Test%20Runner-orange)

An end-to-end test automation framework for the [SAT Japan] vehicle selling platform, built with Python, Playwright, and pytest.

---

## About the Project

This framework automates core workflows on the SAT Japan platform, including:

- **Sell My Car Module:** Price quote, listing, auction
- **Car Services Module:** Auction, Shipping Schedule, Warranty, Storage, Finance, Car Carrier, Customs Clearance, Pre‑Export Inspection, Marine Insurance, Non‑Stolen Vehicle
- **About Us Module:** Company info, loyalty program, SAT Pro membership
- **Buy Flow (End‑to‑End):** Complete order placement from car selection to payment confirmation

It covers positive and negative test scenarios, following the Page Object Model (POM) design pattern for clean, maintainable test code.

---

## Tech Stack

| Tool | Purpose |
|------|---------|
| Python 3.11+ | Programming language |
| Playwright | Browser automation |
| pytest | Test runner |
| pytest-html | HTML test reports |
| pytest-rerunfailures | Auto-retry failed tests |
| python-dotenv | Secure credentials management |

---

## Project Structure
```
SAT_Automation/
├── data/
│   └── list_on_sat_data.py      # Data-driven List on SAT vehicle records
│
├── assets/
│   └── images/                 # Test images for form uploads
│
├── pages/
│   ├── auth/
│   │   └── login_page.py       # Login page actions
│   ├── about_us/               # About Us module page objects
│   ├── buy_flow/               # End‑to‑end order placement page objects
│   ├── car_services/           # Car Services module page objects
│   └── sell_my_car/            # Sell My Car module page objects
│
├── reports/
│   ├── report.html             # Generated HTML test report
│   └── screenshots/            # Auto‑captured screenshots on test failure
│
├── tests/
│   ├── about_us/               # About Us tests
│   ├── buy_flow/               # End‑to‑end order placement tests
│   ├── car_services/           # Car Services tests
│   └── sell_my_car/            # Sell My Car tests (positive and negative)
│
├── .env
├── .gitignore
├── config.py
├── conftest.py
├── pytest.ini
├── run_tests.bat               # Windows batch file to run tests with menu
└── README.md
```

### Buy Now organization

Buy Now automation is organized by business role, vehicle type, and payment
flow:

```text
tests/buy_flow/
|-- user/
|   |-- used_car/
|   |   |-- test_paygent.py
|   |   `-- test_bank_transfer.py
|   `-- new_car/
|       |-- test_paygent.py
|       `-- test_bank_transfer.py
`-- dealer/
    |-- used_car/
    `-- new_car/
```

Only implemented coverage contains test modules. User Paygent and Bank Transfer
flows are implemented for both Used Cars and New Cars. Dealer packages remain
prepared for later coverage and do not report false placeholder tests.

User New Car coverage currently includes:

- **Paygent:** Nissan Dayz X with variant and price checks across details,
  checkout, payment, and the final `Partial Payment` order summary.
- **Bank Transfer:** Honda N-WGN G with variant and price checks plus final
  `Pending` status, `Ask` shipping/total, Track Your Order, Add Payment Proof,
  and bank-information verification.

Each payment method is a separate pytest item. If one payment flow fails, its
automatic rerun does not rerun the other payment method.

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
pip install -r requirements.txt
playwright install
```

### 4. Create .env file

Copy the provided environment template:

```powershell
# Windows
Copy-Item .env.example .env
```

```bash
# Mac/Linux
cp .env.example .env
```

Then update `.env` with your credentials and the environment used for direct
`pytest` commands. The Windows test runner asks for Sprint or Development and
overrides `BASE_URL` for that run:

```
BASE_URL=https://sprint.shineauto.info
LOGIN_EMAIL=your_email@example.com
LOGIN_PASSWORD=your_password
```

The Buy Flow builds its inventory URLs from `BASE_URL` and these stable paths:

```text
USED_CAR_PAYGENT_PATH=/used-cars/mk_volkswagen?sort_by=new_arrival&per_page=25&page=1&unreserved=1
USED_CAR_BANK_PATH=/used-cars/mk_daihatsu?sort_by=new_arrival&per_page=25&page=1&unreserved=1
```

Keep records that expire or change frequently in the same private `.env` file.
This is the only active environment file and is ignored by Git:

```text
AUCTION_CALCULATOR_STOCK_ID=your_current_auction stock ID
NON_STOLEN_VEHICLE_STOCK_ID=your_current stock ID for Non-Stolen verification
```

Update these stock IDs before a state-changing regression run whenever the
configured records are no longer available. The Buy Flow automatically selects
a visible, unreserved vehicle from its payment-specific inventory URL.
---

## How to Run Tests

### Run all tests:
```
pytest -v -s
```

Tests that create orders, payments, listings, quotes, auctions, or other
submissions run without an additional enable prompt.

### Run specific modules:
#### Sell My Car module
```
pytest tests/sell_my_car/ -v -s
```
#### Car Services module
```
pytest tests/car_services/ -v -s
```
#### Using batch files (Windows):
```
.\run_tests.bat
```

The Buy Now menu provides separate User-flow choices:

- **9:** Used Car Buy Now only
- **10:** New Car Buy Now only
- **11:** Combined Used Car and New Car Buy Now

To run only the User New Car Bank Transfer test:

```powershell
$env:BASE_URL="https://development.satjapan.info"
venv\Scripts\pytest.exe tests\buy_flow\user\new_car\test_bank_transfer.py -v -s
```

`run_tests.bat` lets you select Sprint or Development at runtime. The same test
paths and page objects are used for either domain.

---

## Test Cases Summary

| Module | Tests | Description |
|--------|-------|-------------|
| **Sell My Car** | 7 | Price quote, 2 active data-driven List on SAT cases, auction, and negative validation tests |
| **Car Services** | 34 | Auction, Shipping Schedule, Warranty, Storage, Finance, Car Carrier, Customs Clearance, Pre‑Export Inspection, Marine Insurance, Non‑Stolen Vehicle |
| **About Us** | 10 | About SAT, Company Profile, Why Choose SAT, Privacy Policy, Terms & Conditions, Shipping Agents, Loyalty Program (logged in/out), Join SAT Pro (logged in/out) |
| **Buy Flow (End‑to‑End)** | 4 | Independent Used/New Car Paygent and Bank Transfer order flows |
| **Total** | **55** | |

### Module Breakdown

- **Sell My Car:** 7 tests
- **Car Services:** 34 tests
- **About Us:** 10 tests
- **Buy Flow (End‑to‑End):** 4 tests

---

## Key Features

- Page Object Model (POM) – Clean separation of page logic
- Secure credentials – Login details stored in `.env` file, never hardcoded
- Session‑based login – Reuses the authenticated browser-context session
- Auto screenshots – Captures screenshots on any test failure
- Parameterized tests – Runs multiple data sets efficiently
- Independent test items – Retries only the failed flow or verification
- Readiness checks – Uses Playwright waits and bounded stabilization where the
  application recalculates payment totals
- Environment recovery – Detects transient homepage HTTP 500 responses,
  retries a bounded number of times, and returns profile redirects to the
  selected environment homepage before header navigation


---

## Reports

After running tests, open the HTML report:
```
reports/report.html
```

The report includes pass/fail status, test duration, and screenshots for any failed test.

---

## pytest Configuration
The pytest.ini file includes:
```
[pytest]
testpaths = tests
addopts = -v -rR --html=reports/report.html --self-contained-html --reruns 1 --reruns-delay 2
```
--reruns 1 - Retry each failed test once

--reruns-delay 2 - Wait 2 seconds between retries

-rR - Show which individual test items were rerun in the terminal summary

---
## Future Plans

- Add negative test cases for List on SAT and Auction with SAT
- Expand to other site modules (Buy, Search, User Profile)
- Add pytest markers for smoke and regression test groups
- Integrate with GitHub Actions for CI/CD
- Add headless mode for faster execution in CI/CD pipelines
- Generate Allure reports for richer test reporting
