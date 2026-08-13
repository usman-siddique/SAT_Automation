from playwright.sync_api import Error as PlaywrightError, Page, Response

from config import BASE_URL


HOME_LOAD_ATTEMPTS = 3
HOME_RETRY_DELAY_MS = 1000
BACKEND_ERROR_MESSAGES = (
    "Call to a member function first() on array",
    "Whoops, looks like something went wrong",
)


def _backend_error(page: Page, response: Response | None):
    """Return a useful reason when the application served an error page."""
    if response is not None and response.status >= 500:
        return f"HTTP {response.status}"

    body_text = page.locator("body").inner_text(timeout=3000)
    for message in BACKEND_ERROR_MESSAGES:
        if message.lower() in body_text.lower():
            return message
    return None


def open_site_home(page: Page):
    """Open a real homepage, retrying transient Development error pages."""
    last_error = "unknown homepage error"

    for attempt in range(1, HOME_LOAD_ATTEMPTS + 1):
        try:
            response = page.goto(BASE_URL, wait_until="domcontentloaded")
            last_error = _backend_error(page, response) or ""

            if not last_error:
                page.locator("header").wait_for(state="visible", timeout=10000)
                return page
        except (PlaywrightError, AssertionError) as error:
            last_error = str(error)

        if attempt < HOME_LOAD_ATTEMPTS:
            print(
                "Homepage did not load correctly "
                f"(attempt {attempt}/{HOME_LOAD_ATTEMPTS}: {last_error}). Retrying..."
            )
            page.wait_for_timeout(HOME_RETRY_DELAY_MS)

    raise AssertionError(
        f"{BASE_URL} did not return a usable homepage after "
        f"{HOME_LOAD_ATTEMPTS} attempts. Last error: {last_error}"
    )
