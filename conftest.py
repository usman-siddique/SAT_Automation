# ============================================================
# conftest.py
# pytest automatically loads this file -- no need to import it.
# It does two things:
# 1. Provides the 'page' fixture to all test files
# 2. Takes a screenshot if any test fails and attaches it to the HTML report
# ============================================================

import pytest
import os
from playwright.sync_api import sync_playwright
from pages.login_page import LoginPage

# --- Base directory (folder where conftest.py lives) ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# --- Screenshots directory ---
SCREENSHOTS_DIR = os.path.join(BASE_DIR, "reports", "screenshots")


# ============================================================
# Helper: Check if user is actually logged in
# ============================================================

def is_logged_in(page):
    try:
        sign_in = page.locator("header").get_by_role("link", name="Sign in")
        return not sign_in.is_visible(timeout=3000)
    except:
        return False


# ============================================================
# Fixture: Browser Setup & Teardown
# Uses domcontentloaded for faster page loads
# Waits for specific elements instead of full page load
# ============================================================

@pytest.fixture(scope="session")
def page():
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=False)
        context = browser.new_context(viewport=None)
        pg = context.new_page()
        pg.set_default_timeout(30000)

        # Login using LoginPage - all login steps handled in pages/login_page.py
        LoginPage(pg).login()

        yield pg  # test runs here

        context.close()
        browser.close()


# ============================================================
# Hook: Runs automatically after every single test
# If the test failed, captures a screenshot and
# attaches it to the HTML report
# ============================================================

@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()

    if report.when == "call" and report.failed:
        page = item.funcargs.get("page")

        if page:
            try:
                os.makedirs(SCREENSHOTS_DIR, exist_ok=True)
                screenshot_path = os.path.join(SCREENSHOTS_DIR, f"{item.name}.png")
                page.screenshot(path=screenshot_path)
                print(f"📸 Screenshot saved: {screenshot_path}")

                report.extras = getattr(report, "extras", [])
                from pytest_html import extras
                report.extras.append(extras.image(f"screenshots/{item.name}.png"))
            except Exception as e:
                print(f"⚠️ Could not take screenshot: {e}")