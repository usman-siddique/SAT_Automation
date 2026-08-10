import pytest
import os
from playwright.sync_api import sync_playwright
from pages.auth.login_page import LoginPage
from config import BASE_URL

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SCREENSHOTS_DIR = os.path.join(BASE_DIR, "reports", "screenshots")
@pytest.fixture
def require_state_changing_tests():
    """Compatibility fixture for tests that can create external records."""
    pass


def is_logged_in(page):
    try:
        sign_in = page.locator("header").get_by_role("link", name="Sign in")
        return not sign_in.is_visible(timeout=3000)
    except:
        return False


# ============================================================
# Fixture: Browser Setup – supports multiple browsers
# Set BROWSER environment variable to 'chromium' (default), 'firefox', or 'webkit'
# ============================================================

@pytest.fixture(scope="session")
def context():
    headless = os.getenv("HEADLESS", "false").lower() == "true"
    browser_name = os.getenv("BROWSER", "chromium").lower()
    with sync_playwright() as playwright:
        if browser_name == "firefox":
            browser = playwright.firefox.launch(headless=headless)
        elif browser_name == "webkit":
            browser = playwright.webkit.launch(headless=headless)
        else:
            browser = playwright.chromium.launch(headless=headless)
        viewport = {"width": 1280, "height": 720} if headless else None
        ctx = browser.new_context(viewport=viewport)
        yield ctx
        ctx.close()
        browser.close()


# ============================================================
# Fixture: For tests that require login
# ============================================================

@pytest.fixture(scope="function")
def page(context):
    pg = context.new_page()
    pg.set_default_timeout(30000)
    LoginPage(pg).login()
    yield pg
    pg.close()


# ============================================================
# Fixture: For tests that do NOT require login
# ============================================================

@pytest.fixture(scope="function")
def page_no_login(context):
    pg = context.new_page()
    pg.set_default_timeout(30000)
    pg.goto(BASE_URL, wait_until="domcontentloaded")
    yield pg
    pg.close()


# ============================================================
# Hook: Takes screenshot on test failure
# ============================================================

@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()

    if report.when == "call" and report.failed:
        page = item.funcargs.get("page") or item.funcargs.get("page_no_login")
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
