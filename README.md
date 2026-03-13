# SAT Japan - Test Automation Framework

An end-to-end test automation framework for the [SAT Japan](https://development.satjapan.info) vehicle selling platform, built with Python, Playwright, and pytest.

---

## About the Project

This framework automates the core selling workflows on the SAT Japan platform, including:
- Getting a price quote for a vehicle
- Listing a vehicle for sale
- Auctioning a vehicle

It covers both positive (happy path) and negative (validation) test scenarios, following the Page Object Model (POM) design pattern for clean and maintainable test code.

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
│   └── images/          # Test images for form uploads
├── pages/
│   ├── login_page.py    # Login page actions
│   └── sell_page.py     # Sell My Car page actions
├── reports/
│   ├── report.html      # Generated HTML test report
│   └── screenshots/     # Auto-captured screenshots on test failure
├── tests/
│   ├── test_sell.py          # Positive test cases
│   └── test_sell_negative.py # Negative test cases
├── .env                 # Credentials (not pushed to GitHub)
├── .gitignore
├── config.py            # All test data and settings
├── conftest.py          # Browser setup, login fixture, screenshot on failure
├── pytest.ini           # pytest configuration
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

## Test Cases

### Positive Tests (test_sell.py)

| Test | Description |
|------|-------------|
| test_get_price_quote | Completes all 3 steps of Get Price Quote and verifies success |
| test_list_on_sat[list_data0] | Lists a Toyota AQUA from United Kingdom |
| test_list_on_sat[list_data1] | Lists a Nissan Fairlady Z from Thailand |
| test_list_on_sat[list_data2] | Lists a Honda FIT from Australia |
| test_auction_with_sat | Submits a vehicle for auction and verifies success |

### Negative Tests (test_sell_negative.py)

| Test | Description |
|------|-------------|
| test_get_price_quote_empty_fields | All fields empty - verifies all error messages appear |
| test_get_price_quote_partial_validation | Only Year filled - verifies Make and Model errors appear |
| test_get_price_quote_terms_validation | Terms checkbox unchecked - verifies terms error appears |

---

## Key Features

- Page Object Model (POM) - Each page has its own class
- Secure credentials - Login details stored in .env file, never hardcoded
- Relative paths - Works on any machine without changing file paths
- Session-based login - Logs in once and reuses session across all tests
- Auto screenshots - Captures and attaches screenshots on any test failure
- Parametrized tests - List on SAT runs with 3 different data sets automatically
- Positive and negative tests - Covers both happy path and validation scenarios

---

## Reports

After running tests, open the HTML report:
```
SAT_Automation/reports/report.html
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
