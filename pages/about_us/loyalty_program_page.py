from urllib.parse import urlparse


class LoyaltyProgramPage:
    PATH = "/loyalty-program"
    MASTER_WELCOME = "USM USER QA USER, you're at Master Level 3!"
    PRO_WELCOME = "QA Testing User, you're at SAT Pro!"
    LOCK_ASSET = "sat--prolock.webp"
    UNLOCK_ASSET = "sat--pro-unlock.webp"

    HEADINGS = (
        "Enjoy Exclusive Rewards for Being a Master",
        "Buy More For Less With Master",
        "Master Levels in Details",
        "Frequently Asked Questions",
    )
    BENEFIT_CARDS = (
        (
            "Create an account",
            "Earn 50 loyalty points and avail free car insurance and "
            "pre-export inspection service on your first order",
            "Master Level 1",
        ),
        (
            "Make two orders in two years",
            "Avail multiple free car services on a single order and "
            "discounts on other services",
            "Master Level 2",
        ),
        (
            "Make five orders in five years",
            "Avail multiple free and discounted car services along with "
            "priority support from SAT",
            "Master Level 3",
        ),
        (
            "Make a monthly payment of 19.99$",
            "Unlock special discounts on all services and get priority "
            "customer support on every order",
            "SAT Pro",
        ),
    )
    FAQS = (
        (
            "Which orders contribute to my progress in the loyalty program?",
            "All orders of cars will contribute",
        ),
        (
            "How are the loyalty program discounts applied?",
            "discounts are applied automatically",
        ),
        (
            "Why is my Master level different on different devices?",
            "logged into the same account",
        ),
        (
            "Can my Master Level decrease from the one I currently have "
            "once I have unlocked it?",
            "you cannot go down to another level",
        ),
        (
            "What is SAT Pro and how does it work?",
            "$19.99/month",
        ),
        (
            "Can I cancel my SAT Pro subscription anytime?",
            "cancel your subscription anytime",
        ),
    )
    LEVEL_DETAIL_TEXT = (
        "Free Pre-export Inspection Service",
        "Free Insurance Service",
        "Earn 50 Loyalty Points",
        "30 Days Storage Service",
        "20% Off on Non Stolen Check",
        "20% Off on Marine Insurance",
        "20% Off on Auction Payment",
        "Reserve Without Payment",
        "25% off on Car Carrier Service",
        "25% Off on Custom Clearance",
        "Dedicated Auction Agent",
        "Free OBL amendment",
        "Priority Support Service",
        "Free Finance Service",
        "Become a SAT Pro by paying a monthly subscription of $19.99 only",
    )

    def __init__(self, page):
        self.page = page

    def _wait_until_ready(self):
        self.page.get_by_role(
            "heading",
            name="Enjoy Exclusive Rewards for Being a Master",
            exact=True,
        ).wait_for(state="visible")
        assert urlparse(self.page.url).path.rstrip("/") == self.PATH

    def go_to_loyalty_program(self):
        menu = self.page.locator("p.cnm-cls:has-text('About Us')").locator("..")
        menu.hover()
        link = menu.locator(
            ".dropdown_content_header a[href$='/loyalty-program']"
        )
        link.wait_for(state="visible")
        link.click()
        self.page.wait_for_url("**/loyalty-program", wait_until="domcontentloaded")
        self._wait_until_ready()

    def go_to_loyalty_program_mobile(self):
        self.page.locator(
            "#menu_logo_mobile span[data-bs-target='#sidebarmobile']"
        ).click()
        main_menu = self.page.locator("#sidebarmobile")
        main_menu.locator("a.main-items-sidebar-content").filter(
            has_text="Loyalty Program"
        ).click()

        submenu = self.page.locator("#offcanvasLoyaltyProgram")
        link = submenu.locator("a[href$='/loyalty-program']")
        link.wait_for(state="visible")
        link.click()
        self.page.wait_for_url("**/loyalty-program", wait_until="domcontentloaded")
        self._wait_until_ready()

    def _visible_benefit_cards(self):
        return self.page.locator(".benfit-card-more:visible")

    @staticmethod
    def _normalized_text(locator):
        return " ".join(locator.inner_text().split())

    @staticmethod
    def _assert_image_loaded(image, label):
        image.scroll_into_view_if_needed()
        image.wait_for(state="visible")
        loaded = image.evaluate(
            "image => image.complete && image.naturalWidth > 0"
        )
        assert loaded, f"{label} image did not load"

    def verify_page_content(self):
        for heading in self.HEADINGS:
            visible_headings = self.page.get_by_role(
                "heading", name=heading, exact=True
            ).filter(visible=True)
            assert visible_headings.count() == 1, (
                f"Loyalty heading is missing or duplicated: {heading}"
            )

        sat_pro_heading = self.page.locator("h2:visible").filter(
            has_text="SAT PRO"
        )
        assert sat_pro_heading.count() >= 1, "SAT PRO section heading is missing"

        page_text = self._normalized_text(self.page.locator("body"))
        for detail in self.LEVEL_DETAIL_TEXT:
            assert detail in page_text, (
                f"Loyalty level details are missing expected text: {detail}"
            )

        cards = self._visible_benefit_cards()
        assert cards.count() == len(self.BENEFIT_CARDS), (
            f"Expected {len(self.BENEFIT_CARDS)} visible benefit cards, "
            f"found {cards.count()}"
        )
        for index, (title, description, badge) in enumerate(self.BENEFIT_CARDS):
            text = self._normalized_text(cards.nth(index))
            for expected in (title, description, badge):
                assert expected in text, (
                    f"{badge} card is missing expected text: {expected}"
                )

    def _verify_sat_pro_link(self):
        sat_pro_link = self.page.locator("a[href$='/sat-pro']:visible")
        assert sat_pro_link.count() >= 1, "SAT Pro detail link is missing"
        href = sat_pro_link.first.get_attribute("href")
        assert urlparse(href).path == "/sat-pro"
        response = self.page.request.get(
            href,
            fail_on_status_code=False,
            timeout=30000,
        )
        assert response.status < 400, (
            f"SAT Pro link returned HTTP {response.status}: {href}"
        )
        assert urlparse(response.url).path.rstrip("/") == "/sat-pro", (
            f"SAT Pro link redirected unexpectedly: {response.url}"
        )

    def verify_all_faqs(self):
        buttons = self.page.locator("button.accordion-button:visible")
        expected_questions = [question for question, _ in self.FAQS]
        faq_buttons = []
        for index in range(buttons.count()):
            button = buttons.nth(index)
            if self._normalized_text(button) in expected_questions:
                faq_buttons.append(button)

        assert len(faq_buttons) == len(self.FAQS), (
            f"Expected {len(self.FAQS)} visible FAQs, found {len(faq_buttons)}"
        )
        for button, (question, answer_text) in zip(faq_buttons, self.FAQS):
            assert self._normalized_text(button) == question
            target = button.get_attribute("data-bs-target")
            assert target, f"FAQ has no answer target: {question}"
            button.click()
            panel = self.page.locator(target)
            panel.wait_for(state="visible")
            answer = self._normalized_text(panel)
            assert answer_text.lower() in answer.lower(), (
                f"FAQ answer is incorrect or empty: {question}"
            )
            assert button.get_attribute("aria-expanded") == "true"

    def _assert_card_lock_states(self, expected_assets):
        cards = self._visible_benefit_cards()
        assert len(expected_assets) == cards.count()
        for index, expected_asset in enumerate(expected_assets):
            badge = self.BENEFIT_CARDS[index][2]
            icon = cards.nth(index).locator("img[alt='lock']")
            assert icon.count() == 1, f"{badge} lock-state icon is missing"
            source = icon.get_attribute("src") or ""
            assert expected_asset in source, (
                f"{badge} has the wrong lock state: {source}"
            )
            self._assert_image_loaded(icon, f"{badge} lock state")

    def verify_logged_out_state(self):
        self.verify_page_content()
        self._verify_sat_pro_link()
        assert self.page.get_by_role(
            "heading",
            name="Unlock More Benefits With Our Loyalty Program",
            exact=True,
        ).filter(visible=True).count() == 1, (
            "Guest Loyalty introduction is missing"
        )
        self._assert_card_lock_states([self.LOCK_ASSET] * 4)
        self.verify_all_faqs()

        sign_up = self.page.get_by_role(
            "link", name="Sign Up - It's Free", exact=True
        ).filter(visible=True)
        assert sign_up.count() == 1, "Guest Sign Up link is missing"
        assert urlparse(sign_up.get_attribute("href")).path == "/login"
        sign_up.click()
        self.page.wait_for_url("**/login", wait_until="domcontentloaded")
        self.page.locator("#login_email").wait_for(state="visible")

    def verify_mobile_logged_out_state(self):
        self.verify_page_content()
        assert self.page.get_by_role(
            "heading",
            name="Unlock More Benefits With Our Loyalty Program",
            exact=True,
        ).filter(visible=True).count() == 1, (
            "Mobile Loyalty introduction is missing"
        )
        self._assert_card_lock_states([self.LOCK_ASSET] * 4)
        self.verify_all_faqs()

        layout = self.page.evaluate(
            """() => ({
                viewportWidth: visualViewport.width,
                documentWidth: document.documentElement.scrollWidth,
                cards: [...document.querySelectorAll('.benfit-card-more')]
                    .filter(card => card.offsetParent !== null)
                    .map(card => {
                        const box = card.getBoundingClientRect();
                        return {left: box.left, right: box.right, width: box.width};
                    })
            })"""
        )
        assert layout["documentWidth"] <= layout["viewportWidth"], (
            f"Loyalty page has horizontal mobile overflow: {layout}"
        )
        for box in layout["cards"]:
            assert box["left"] >= 0 and box["right"] <= layout["viewportWidth"], (
                f"A Loyalty benefit card is clipped on mobile: {box}"
            )

    def verify_member_state(self, expected_welcome, expected_assets):
        self.verify_page_content()
        self._verify_sat_pro_link()
        welcome = self.page.locator("h2.login-sat-user:visible")
        welcome.wait_for(state="visible")
        assert self._normalized_text(welcome) == expected_welcome
        self._assert_card_lock_states(expected_assets)

    def verify_master_level_three_state(self):
        self.verify_member_state(
            self.MASTER_WELCOME,
            [self.UNLOCK_ASSET] * 3 + [self.LOCK_ASSET],
        )

    def verify_sat_pro_member_state(self):
        self.verify_member_state(
            self.PRO_WELCOME,
            [self.UNLOCK_ASSET] * 4,
        )
