# SAT Japan - Test Automation Framework

![Python](https://img.shields.io/badge/Python-3.11-blue)
![Playwright](https://img.shields.io/badge/Playwright-Test%20Automation-green)
![Pytest](https://img.shields.io/badge/Pytest-Test%20Runner-orange)

An end-to-end test automation framework for the [SAT Japan](https://development.satjapan.info) vehicle selling platform, built with Python, Playwright, and pytest.

---

## About the Project

This framework automates core workflows on the SAT Japan platform, including:

- **Sell My Car Module:** Price quote, listing, auction
- **Car Services Module:** Auction, Shipping Schedule, Insurance, Storage, Finance, Car Carrier, Customs Clearance, Pre‑Export Inspection, Marine Insurance, Non‑Stolen Vehicle
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
pip install playwright pytest pytest-html pytest-rerunfailures python-dotenv
playwright install
```

### 4. Create .env file

Create a .env file inside the SAT_Automation/ folder:
```
BASE_URL=https://development.satjapan.info
LOGIN_EMAIL=your_email@example.com
LOGIN_PASSWORD=your_password
```
---

## How to Run Tests

### Run all tests:
```
pytest -v -s
```
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
---

## Test Cases Summary

| Module | Tests | Description |
|--------|-------|-------------|
| **Sell My Car** | 8 | Positive and negative tests for price quote, listing, auction |
| **Car Services** | 17 | Auction, Shipping Schedule, Insurance, Storage, Finance, Car Carrier, Customs Clearance, Pre‑Export Inspection, Marine Insurance, Non‑Stolen Vehicle |
| **About Us** | 10 | About SAT, Company Profile, Why Choose SAT, Privacy Policy, Terms & Conditions, Shipping Agents, Loyalty Program (logged in/out), Join SAT Pro (logged in/out) |
| **Buy Flow (End‑to‑End)** | 1 | Complete order placement from car selection to payment confirmation |
| **Total** | **36** | |

### Module Breakdown

- **Sell My Car:** 8 tests
- **Car Services:** 17 tests
- **About Us:** 10 tests
- **Buy Flow (End‑to‑End):** 1 test

---

## Key Features

- Page Object Model (POM) – Clean separation of page logic
- Secure credentials – Login details stored in `.env` file, never hardcoded
- Session‑based login – Logs in once and reuses session across all tests
- Auto screenshots – Captures screenshots on any test failure
- Parameterized tests – Runs multiple data sets efficiently
- Proper waits – No hardcoded sleeps; uses Playwright’s built‑in wait methods


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
addopts = -v --html=reports/report.html --self-contained-html --reruns 2 --reruns-delay 2
```
--reruns 2 - Retry failed tests up to 2 times

--reruns-delay 2 - Wait 2 seconds between retries

---
## Future Plans

- Add negative test cases for List on SAT and Auction with SAT
- Expand to other site modules (Buy, Search, User Profile)
- Add pytest markers for smoke and regression test groups
- Integrate with GitHub Actions for CI/CD
- Add headless mode for faster execution in CI/CD pipelines
- Generate Allure reports for richer test reporting
