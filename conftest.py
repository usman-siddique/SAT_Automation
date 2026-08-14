import os

import pytest
from playwright.sync_api import sync_playwright

from config import DEALER_LOGIN_EMAIL, DEALER_LOGIN_PASSWORD
from pages.auth.login_page import LoginPage
from pages.site_navigation import open_site_home


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SCREENSHOTS_DIR = os.path.join(BASE_DIR, "reports", "screenshots")


@pytest.fixture
def require_state_changing_tests():
    """Compatibility fixture for tests that can create external records."""
    pass


def _context_options():
    headless = os.getenv("HEADLESS", "false").lower() == "true"
    if headless:
        return {"viewport": {"width": 1280, "height": 720}}
    return {"viewport": None}


@pytest.fixture(scope="session")
def browser():
    """Launch one browser per pytest worker; role contexts remain isolated."""
    headless = os.getenv("HEADLESS", "false").lower() == "true"
    browser_name = os.getenv("BROWSER", "chromium").lower()

    with sync_playwright() as playwright:
        if browser_name == "firefox":
            launched_browser = playwright.firefox.launch(headless=headless)
        elif browser_name == "webkit":
            launched_browser = playwright.webkit.launch(headless=headless)
        else:
            launched_browser = playwright.chromium.launch(headless=headless)

        yield launched_browser
        launched_browser.close()


@pytest.fixture(scope="session")
def user_context(browser):
    """Cookie/local-storage boundary reserved for the normal User account."""
    ctx = browser.new_context(**_context_options())
    yield ctx
    ctx.close()


@pytest.fixture(scope="session")
def context(user_context):
    """Backward-compatible alias used by existing User page objects/tests."""
    return user_context


@pytest.fixture(scope="session")
def dealer_context(browser):
    """Independent cookie/local-storage boundary for future Dealer tests."""
    ctx = browser.new_context(**_context_options())
    yield ctx
    ctx.close()


@pytest.fixture(scope="function")
def page(context):
    """Existing authenticated User fixture; test signatures stay unchanged."""
    pg = context.new_page()
    pg.set_default_timeout(30000)
    try:
        LoginPage(pg).login(account_label="User")
        yield pg
    finally:
        if not pg.is_closed():
            pg.close()


@pytest.fixture(scope="function")
def dealer_page(dealer_context):
    """Authenticated Dealer page with a session isolated from User tests."""
    if not DEALER_LOGIN_EMAIL or not DEALER_LOGIN_PASSWORD:
        raise RuntimeError(
            "Dealer credentials are missing. Set DEALER_LOGIN_EMAIL and "
            "DEALER_LOGIN_PASSWORD in the private .env file."
        )

    pg = dealer_context.new_page()
    pg.set_default_timeout(30000)
    try:
        LoginPage(pg).login(
            email=DEALER_LOGIN_EMAIL,
            password=DEALER_LOGIN_PASSWORD,
            account_label="Dealer",
        )
        yield pg
    finally:
        if not pg.is_closed():
            pg.close()


@pytest.fixture(scope="function")
def page_no_login(browser):
    """Fresh anonymous context per test; authenticated cookies cannot leak."""
    anonymous_context = browser.new_context(**_context_options())
    pg = anonymous_context.new_page()
    pg.set_default_timeout(30000)
    try:
        open_site_home(pg)
        yield pg
    finally:
        if not pg.is_closed():
            pg.close()
        anonymous_context.close()


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Capture the relevant User, Dealer, or anonymous page on failure."""
    outcome = yield
    report = outcome.get_result()

    if report.when == "call" and report.failed:
        active_page = (
            item.funcargs.get("page")
            or item.funcargs.get("dealer_page")
            or item.funcargs.get("page_no_login")
        )
        if active_page:
            try:
                os.makedirs(SCREENSHOTS_DIR, exist_ok=True)
                screenshot_path = os.path.join(
                    SCREENSHOTS_DIR,
                    f"{item.name}.png",
                )
                active_page.screenshot(path=screenshot_path)
                print(f"Screenshot saved: {screenshot_path}")

                report.extras = getattr(report, "extras", [])
                from pytest_html import extras

                report.extras.append(
                    extras.image(f"screenshots/{item.name}.png")
                )
            except Exception as error:
                print(f"Could not take screenshot: {error}")
