from config import LOGIN_EMAIL, LOGIN_PASSWORD
from pages.site_navigation import open_site_home


class LoginPage:
    def __init__(self, page):
        self.page = page

    def login(self):
        # A Laravel error page must never be mistaken for an authenticated
        # session merely because it has no Sign in link.
        open_site_home(self.page)

        # On a confirmed homepage, no Sign in link means this browser context
        # already has an authenticated session.
        sign_in_btn = self.page.locator("header").get_by_role(
            "link", name="Sign in"
        )
        if not sign_in_btn.is_visible(timeout=3000):
            print("Already logged in, skipping login")
            return

        sign_in_btn.click()

        email = self.page.locator("#login_email")
        email.wait_for(state="visible")
        email.fill(LOGIN_EMAIL)
        self.page.get_by_role("button", name="Continue").click()

        password = self.page.locator("input[type='password']")
        password.wait_for(state="visible")
        password.fill(LOGIN_PASSWORD)
        self.page.get_by_role("button", name="Login").click()

        self.page.wait_for_function(
            "() => !window.location.pathname.startsWith('/login')",
            timeout=30000,
        )

        # Login may redirect to a profile/dashboard. Return to a verified
        # public homepage so every test starts from the same navigation state.
        open_site_home(self.page)
        sign_in_btn = self.page.locator("header").get_by_role(
            "link", name="Sign in"
        )
        assert not sign_in_btn.is_visible(timeout=3000), (
            "Login did not create an authenticated session."
        )

        print("Login: PASS")
