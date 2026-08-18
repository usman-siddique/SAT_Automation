import os
import platform
import shutil
import sys
from datetime import datetime
from pathlib import Path

import allure
import pytest
from allure_commons.types import AttachmentType
from playwright.sync_api import sync_playwright

from config import (
    BASE_URL,
    DEALER_LOGIN_EMAIL,
    DEALER_LOGIN_PASSWORD,
    ELIGIBLE_DEALER_USER_EMAIL,
    ELIGIBLE_DEALER_USER_PASSWORD,
    REJECTED_DEALER_USER_EMAIL,
    REJECTED_DEALER_USER_PASSWORD,
)
from pages.auth.login_page import LoginPage
from pages.site_navigation import open_site_home


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ALLURE_CONFIG_DIR = Path(BASE_DIR) / "allure_config"


def _humanize(value):
    acronyms = {
        "api": "API",
        "id": "ID",
        "pdf": "PDF",
        "sat": "SAT",
        "url": "URL",
    }
    words = value.removeprefix("test_").replace("_", " ").split()
    return " ".join(acronyms.get(word.lower(), word.capitalize()) for word in words)


def _environment_name():
    if "sprint.shineauto.info" in BASE_URL:
        return "Sprint"
    if "development.satjapan.info" in BASE_URL:
        return "Development"
    return BASE_URL


def _allure_results_dir(config):
    configured_dir = config.getoption("allure_report_dir", default=None)
    if configured_dir:
        return Path(configured_dir).resolve()
    return Path(BASE_DIR) / "reports" / "allure-results"


def pytest_sessionstart(session):
    """Add non-sensitive execution context and failure categories to Allure."""
    if hasattr(session.config, "workerinput"):
        return

    results_dir = _allure_results_dir(session.config)
    results_dir.mkdir(parents=True, exist_ok=True)

    environment = {
        "Application": "SAT Automation",
        "Environment": _environment_name(),
        "Base_URL": BASE_URL,
        "Browser": os.getenv("BROWSER", "chromium").lower(),
        "Headless": os.getenv("HEADLESS", "false").lower(),
        "Operating_System": platform.platform(),
        "Python": sys.version.split()[0],
        "Executed_At": datetime.now().astimezone().isoformat(timespec="seconds"),
    }
    properties = "\n".join(
        f"{key} = {value}" for key, value in environment.items()
    )
    (results_dir / "environment.properties").write_text(
        properties + "\n",
        encoding="utf-8",
    )

    categories_source = ALLURE_CONFIG_DIR / "categories.json"
    if categories_source.exists():
        shutil.copyfile(categories_source, results_dir / "categories.json")


@pytest.fixture(autouse=True)
def allure_test_metadata(request):
    """Give every test a readable business hierarchy and execution labels."""
    test_path = Path(str(request.node.path))
    try:
        relative_path = test_path.relative_to(Path(BASE_DIR) / "tests")
    except ValueError:
        relative_path = test_path

    directories = list(relative_path.parts[:-1])
    module_name = relative_path.stem
    suite_name = _humanize(directories[0] if directories else module_name)

    if len(directories) > 1:
        sub_suite_parts = directories[1:] + [module_name]
    else:
        sub_suite_parts = [module_name]

    allure.dynamic.parent_suite("SAT Automation")
    allure.dynamic.suite(suite_name)
    allure.dynamic.sub_suite(
        " / ".join(_humanize(part) for part in sub_suite_parts)
    )
    allure.dynamic.label("environment", _environment_name())
    allure.dynamic.label("browser", os.getenv("BROWSER", "chromium").lower())


def pytest_runtest_call(item):
    """Set the readable title after Allure finishes its setup-phase naming."""
    allure.dynamic.title(_humanize(item.name))


def _prepare_page(pg, request):
    """Register a page early so setup and test failures can be attached."""
    pg.set_default_timeout(30000)
    request.node._sat_active_page = pg
    request.node._sat_browser_messages = []
    # pytest-rerunfailures reuses the same test Item for every attempt.
    # Reset attachment tracking so the final retry also receives evidence.
    request.node._sat_evidence_attached_phases = set()

    def capture_console(message):
        if message.type in ("warning", "error"):
            request.node._sat_browser_messages.append(
                f"CONSOLE {message.type.upper()}: {message.text}"
            )

    def capture_page_error(error):
        request.node._sat_browser_messages.append(f"PAGE ERROR: {error}")

    pg.on("console", capture_console)
    pg.on("pageerror", capture_page_error)
    return pg


def _attach_browser_evidence(item, active_page, phase):
    """Attach useful browser diagnostics without exposing environment secrets."""
    attached_phases = getattr(item, "_sat_evidence_attached_phases", set())
    if phase in attached_phases:
        return
    attached_phases.add(phase)
    item._sat_evidence_attached_phases = attached_phases

    if active_page and not active_page.is_closed():
        try:
            allure.attach(
                active_page.screenshot(full_page=True),
                name=f"Failure screenshot ({phase})",
                attachment_type=AttachmentType.PNG,
            )
            allure.attach(
                active_page.url,
                name="Failure URL",
                attachment_type=AttachmentType.TEXT,
            )
        except Exception as error:
            print(f"Could not attach browser evidence: {error}")

    browser_messages = getattr(item, "_sat_browser_messages", [])
    if browser_messages:
        allure.attach(
            "\n".join(browser_messages),
            name="Browser warnings and errors",
            attachment_type=AttachmentType.TEXT,
        )


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
def eligible_dealer_user_context(browser):
    """Isolated session for a User who can apply to become a Dealer."""
    ctx = browser.new_context(**_context_options())
    yield ctx
    ctx.close()


@pytest.fixture(scope="session")
def rejected_dealer_user_context(browser):
    """Isolated session for a User whose Dealer application was rejected."""
    ctx = browser.new_context(**_context_options())
    yield ctx
    ctx.close()


@pytest.fixture(scope="session")
def dealer_context(browser):
    """Independent cookie/local-storage boundary for future Dealer tests."""
    ctx = browser.new_context(**_context_options())
    yield ctx
    ctx.close()


@pytest.fixture(scope="function")
def page(context, request):
    """Existing authenticated User fixture; test signatures stay unchanged."""
    pg = _prepare_page(context.new_page(), request)
    try:
        LoginPage(pg).login(account_label="User")
        yield pg
    except Exception:
        _attach_browser_evidence(request.node, pg, "setup")
        raise
    finally:
        if not pg.is_closed():
            pg.close()


@pytest.fixture(scope="function")
def eligible_dealer_user_page(eligible_dealer_user_context, request):
    """Authenticated User who has not submitted a Dealer application."""
    if not ELIGIBLE_DEALER_USER_EMAIL or not ELIGIBLE_DEALER_USER_PASSWORD:
        raise RuntimeError(
            "Eligible Dealer User credentials are missing. Set "
            "ELIGIBLE_DEALER_USER_EMAIL and ELIGIBLE_DEALER_USER_PASSWORD "
            "in the private .env file."
        )

    pg = _prepare_page(eligible_dealer_user_context.new_page(), request)
    try:
        LoginPage(pg).login(
            email=ELIGIBLE_DEALER_USER_EMAIL,
            password=ELIGIBLE_DEALER_USER_PASSWORD,
            account_label="Eligible Dealer User",
        )
        yield pg
    except Exception:
        _attach_browser_evidence(request.node, pg, "setup")
        raise
    finally:
        if not pg.is_closed():
            pg.close()


@pytest.fixture(scope="function")
def rejected_dealer_user_page(rejected_dealer_user_context, request):
    """Authenticated User whose Dealer application was rejected."""
    if not REJECTED_DEALER_USER_EMAIL or not REJECTED_DEALER_USER_PASSWORD:
        raise RuntimeError(
            "Rejected Dealer User credentials are missing. Set "
            "REJECTED_DEALER_USER_EMAIL and REJECTED_DEALER_USER_PASSWORD "
            "in the private .env file."
        )

    pg = _prepare_page(rejected_dealer_user_context.new_page(), request)
    try:
        LoginPage(pg).login(
            email=REJECTED_DEALER_USER_EMAIL,
            password=REJECTED_DEALER_USER_PASSWORD,
            account_label="Rejected Dealer User",
        )
        yield pg
    except Exception:
        _attach_browser_evidence(request.node, pg, "setup")
        raise
    finally:
        if not pg.is_closed():
            pg.close()


@pytest.fixture(scope="function")
def dealer_page(dealer_context, request):
    """Authenticated Dealer page with a session isolated from User tests."""
    if not DEALER_LOGIN_EMAIL or not DEALER_LOGIN_PASSWORD:
        raise RuntimeError(
            "Dealer credentials are missing. Set DEALER_LOGIN_EMAIL and "
            "DEALER_LOGIN_PASSWORD in the private .env file."
        )

    pg = _prepare_page(dealer_context.new_page(), request)
    try:
        LoginPage(pg).login(
            email=DEALER_LOGIN_EMAIL,
            password=DEALER_LOGIN_PASSWORD,
            account_label="Dealer",
        )
        yield pg
    except Exception:
        _attach_browser_evidence(request.node, pg, "setup")
        raise
    finally:
        if not pg.is_closed():
            pg.close()


@pytest.fixture(scope="function")
def page_no_login(browser, request):
    """Fresh anonymous context per test; authenticated cookies cannot leak."""
    anonymous_context = browser.new_context(**_context_options())
    pg = _prepare_page(anonymous_context.new_page(), request)
    try:
        open_site_home(pg)
        yield pg
    except Exception:
        _attach_browser_evidence(request.node, pg, "setup")
        raise
    finally:
        if not pg.is_closed():
            pg.close()
        anonymous_context.close()


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Attach browser evidence for setup, test, and teardown failures."""
    outcome = yield
    report = outcome.get_result()

    if report.failed:
        active_page = (
            item.funcargs.get("page")
            or item.funcargs.get("eligible_dealer_user_page")
            or item.funcargs.get("rejected_dealer_user_page")
            or item.funcargs.get("dealer_page")
            or item.funcargs.get("page_no_login")
            or getattr(item, "_sat_active_page", None)
        )
        _attach_browser_evidence(item, active_page, report.when)
