from playwright.sync_api import Error as PlaywrightError

from config import BASE_URL, LOGIN_EMAIL, LOGIN_PASSWORD
from pages.site_navigation import open_site_home


LOGIN_ATTEMPTS = 2
LOGIN_RETRY_DELAY_MS = 1000


class LoginPage:
    def __init__(self, page):
        self.page = page

    def _login_once(self, email: str, password: str, account_label: str):
        # A Laravel error page must never be mistaken for an authenticated
        # session merely because it has no Sign in link.
        open_site_home(self.page)

        # Desktop exposes Sign in in the header. Phone profiles keep it inside
        # a closed menu, so use the direct login route when no visible control
        # is available instead of assuming the context is authenticated.
        sign_in_btn = self.page.get_by_role(
            "link", name="Sign in", exact=True
        ).filter(visible=True).first
        if sign_in_btn.is_visible(timeout=3000):
            login_url = sign_in_btn.get_attribute("href") or ""
            assert login_url.endswith("/login"), (
                f"{account_label} Sign in link changed: {login_url}"
            )
            self.page.goto(login_url, wait_until="domcontentloaded")
        else:
            self.page.goto(
                f"{BASE_URL}/login",
                wait_until="domcontentloaded",
            )
            if not self.page.url.startswith(f"{BASE_URL}/login"):
                print(f"{account_label} already logged in, skipping login")
                return self

        email_input = self.page.locator("#login_email")
        email_input.wait_for(state="visible")
        email_input.fill(email)
        self.page.get_by_role("button", name="Continue").click()

        password_input = self.page.locator("input[type='password']")
        password_input.wait_for(state="visible")
        password_input.fill(password)
        self.page.get_by_role("button", name="Login").click()

        self.page.wait_for_function(
            "() => !window.location.pathname.startsWith('/login')",
            timeout=30000,
        )

        # Login may redirect to a profile/dashboard. Return to a verified
        # public homepage so every test starts from the same navigation state.
        open_site_home(self.page)
        assert not self.page.locator("#login_email").is_visible(), (
            f"{account_label} login did not leave the login page."
        )

        print(f"{account_label} login: PASS")
        return self

    def login(
        self,
        email: str | None = None,
        password: str | None = None,
        account_label: str = "User",
    ):
        """Authenticate one isolated role context, preserving User defaults."""
        login_email = email or LOGIN_EMAIL
        login_password = password or LOGIN_PASSWORD
        if not login_email or not login_password:
            raise RuntimeError(
                f"{account_label} login credentials are missing from .env."
            )

        last_error = None
        for attempt in range(1, LOGIN_ATTEMPTS + 1):
            try:
                return self._login_once(
                    login_email,
                    login_password,
                    account_label,
                )
            except (PlaywrightError, AssertionError) as error:
                last_error = error
                if attempt < LOGIN_ATTEMPTS:
                    print(
                        f"{account_label} login attempt {attempt}/"
                        f"{LOGIN_ATTEMPTS} failed. Retrying..."
                    )
                    self.page.wait_for_timeout(LOGIN_RETRY_DELAY_MS)

        raise AssertionError(
            f"{account_label} login failed after {LOGIN_ATTEMPTS} attempts: "
            f"{last_error}"
        ) from last_error

    def register_new_user(self, email: str, password: str, name: str):
        """Create and authenticate a regular User with a unique email."""
        open_site_home(self.page)
        sign_in = self.page.locator("header").get_by_role(
            "link", name="Sign in"
        )
        sign_in.click()

        email_input = self.page.locator("#login_email")
        email_input.wait_for(state="visible")
        email_input.fill(email)
        self.page.get_by_role("button", name="Continue", exact=True).click()

        self.page.wait_for_url("**/sign-up*")
        self.page.locator("#register_name").fill(name)
        self.page.locator("#register_password").fill(password)
        self.page.locator("#register_confirm_password").fill(password)
        self.page.locator("#terms").check()
        self.page.locator("#registerFormBtn").click()

        self.page.wait_for_function(
            "() => !window.location.pathname.startsWith('/sign-up')",
            timeout=30000,
        )
        open_site_home(self.page)
        assert not sign_in.is_visible(timeout=3000), (
            "New User registration did not create an authenticated session."
        )
        return self
