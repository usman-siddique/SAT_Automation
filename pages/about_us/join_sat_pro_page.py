from urllib.parse import urlparse

from config import BASE_URL


class JoinSatProPage:
    PATH = "/sat-pro"
    PAYMENT_PATH = "/sat-pro-payment"
    MEMBERSHIP_PATH = "/sat-pro-membership"

    BENEFIT_COPY = (
        ("Free Car Carrier Service", "Cover damages repairs during delivery"),
        (
            "Free Customs Clearance Service",
            "Ensure fast and compliant shipments",
        ),
        ("Free Car Insurance Service", "Ensure safe vehicle transport"),
        ("Free Storage Service", "Safely store your order for 60 days"),
        ("20% Off on Auction Service", "Bid and win your dream car"),
        ("20% Off on Marine Insurance", "Cover damages during transport"),
        ("20% Off on Stolen Car Check", "Verify car theft before purcahse"),
        (
            "Dedicated Auction Agent",
            "Get support to bid your favorite car",
        ),
        ("Free OBL Amendment", "Make changes to your bill of lading"),
        (
            "Priority Support Service",
            "Get any query answered with 24/7 support",
        ),
    )
    WHY_JOIN_COPY = (
        "Get more SAT Points per order than normal users",
        "Get exclusive discounts on premium car services",
        "Access special cars only available for PRO members",
    )
    FAQ_PREFIXES = (
        "Which orders contribute",
        "How are the loyalty program discounts",
        "Why is my Master level",
        "Can my Master Level decrease",
        "What is SAT Pro",
        "Can | cancel my SAT Pro subscription",
    )
    CANCELLATION_REASONS = (
        "Not saving enough",
        "Issues with my Orders",
        "Not Satisfied with SAT benefits",
        "Want to take break",
        "Something else",
    )

    def __init__(self, page):
        self.page = page

    @staticmethod
    def _normalized_text(locator):
        return " ".join(locator.inner_text().split())

    def _path(self):
        return urlparse(self.page.url).path.rstrip("/") or "/"

    def _join_buttons(self):
        return self.page.get_by_text(
            "Join SAT Pro",
            exact=True,
        ).filter(visible=True)

    def _wait_for_landing(self):
        self.page.locator("h1:visible,h2:visible").filter(
            has_text="SAT Pro"
        ).first.wait_for(state="visible")
        assert self._path() == self.PATH

    def go_to_sat_pro(self):
        menu = self.page.locator("p.cnm-cls:has-text('About Us')").locator("..")
        menu.hover()
        link = menu.locator(".dropdown_content_header a[href$='/sat-pro']")
        link.wait_for(state="visible")
        link.click()
        self.page.wait_for_url("**/sat-pro", wait_until="domcontentloaded")
        self._wait_for_landing()

    def go_to_sat_pro_mobile(self):
        self.page.locator(
            "#menu_logo_mobile span[data-bs-target='#sidebarmobile']"
        ).click()
        self.page.locator("#sidebarmobile a.main-items-sidebar-content").filter(
            has_text="Loyalty Program"
        ).click()
        submenu = self.page.locator("#offcanvasLoyaltyProgram")
        link = submenu.locator("a[href$='/sat-pro']")
        link.wait_for(state="visible")
        link.click()
        self.page.wait_for_url("**/sat-pro", wait_until="domcontentloaded")
        self._wait_for_landing()

    def verify_landing_content(self, include_desktop_hero_copy=True):
        assert self.page.get_by_role(
            "heading",
            name="SAT Pro Benefits",
            exact=True,
        ).filter(visible=True).count() == 1
        body_text = self._normalized_text(self.page.locator("body"))
        required_copy = (
            "Flexible Pricing For All Your Needs",
            "No hidden charges and cancel anytime",
            "$19.99 per month",
            "Save an average of $600 per order with SAT Pro",
            "Why Join SAT Pro",
        )
        if include_desktop_hero_copy:
            required_copy += (
                "Become a SAT Pro member and get exclusive perks and benefits.",
                "Join for just $19.99 /month and cancel anytime.",
            )
        for expected in required_copy + self.WHY_JOIN_COPY:
            assert expected in body_text, (
                f"SAT Pro landing page is missing expected text: {expected}"
            )

        for title, description in self.BENEFIT_COPY:
            assert title in body_text, f"SAT Pro benefit is missing: {title}"
            assert description in body_text, (
                f"SAT Pro benefit description is missing: {description}"
            )

        all_accordion_buttons = self.page.locator(
            "button.accordion-button:visible"
        )
        faq_buttons = []
        for index in range(all_accordion_buttons.count()):
            button = all_accordion_buttons.nth(index)
            question = self._normalized_text(button)
            if question.startswith(self.FAQ_PREFIXES):
                faq_buttons.append(button)

        assert len(faq_buttons) == 6, (
            f"Expected 6 SAT Pro FAQs, found {len(faq_buttons)}"
        )
        for button in faq_buttons:
            target = button.get_attribute("data-bs-target")
            assert target, "A SAT Pro FAQ has no answer target"
            button.click()
            panel = self.page.locator(target)
            panel.wait_for(state="visible")
            assert self._normalized_text(panel), "A SAT Pro FAQ answer is empty"

    def verify_all_guest_join_redirects(self):
        for index in range(3):
            if index:
                self.page.goto(
                    f"{BASE_URL}{self.PATH}",
                    wait_until="domcontentloaded",
                )
                self._wait_for_landing()

            buttons = self._join_buttons()
            assert buttons.count() == 3, (
                f"Expected 3 Join SAT Pro buttons, found {buttons.count()}"
            )
            href = buttons.nth(index).get_attribute("href")
            assert urlparse(href).path == self.PAYMENT_PATH
            buttons.nth(index).click()
            self.page.wait_for_url("**/login*", wait_until="domcontentloaded")
            assert self._path() == "/login", (
                f"Join button {index + 1} did not redirect guests to login"
            )
            self.page.locator("#login_email").wait_for(state="visible")

    def verify_mobile_guest_experience(self):
        self.verify_landing_content(include_desktop_hero_copy=False)
        buttons = self._join_buttons()
        assert buttons.count() == 3, (
            f"Expected 3 mobile Join SAT Pro buttons, found {buttons.count()}"
        )

        layout = self.page.evaluate(
            """() => ({
                viewportWidth: visualViewport.width,
                documentWidth: document.documentElement.scrollWidth,
                buttons: [...document.querySelectorAll("a[href$='/sat-pro-payment']")]
                    .filter(button => button.offsetParent !== null)
                    .map(button => {
                        const box = button.getBoundingClientRect();
                        return {left: box.left, right: box.right, width: box.width};
                    })
            })"""
        )
        assert layout["documentWidth"] <= layout["viewportWidth"], (
            f"SAT Pro has horizontal mobile overflow: {layout}"
        )
        for box in layout["buttons"]:
            assert box["left"] >= 0 and box["right"] <= layout["viewportWidth"], (
                f"A Join SAT Pro button is clipped on mobile: {box}"
            )

        buttons.first.click()
        self.page.wait_for_url("**/login*", wait_until="domcontentloaded")
        assert self._path() == "/login"
        self.page.locator("#login_email").wait_for(state="visible")

    def _verify_mobile_layout(self, page_name, elements):
        # Allow a few CSS pixels for browser rounding/decorative overflow. This
        # avoids reporting invisible 2-5px differences as user-facing defects,
        # while still catching meaningful overflow on narrow mobile viewports.
        overflow_tolerance = 5
        layout = self.page.evaluate(
            """() => ({
                viewportWidth: visualViewport.width,
                documentWidth: document.documentElement.scrollWidth,
                bodyWidth: document.body.scrollWidth
            })"""
        )
        assert layout["documentWidth"] <= (
            layout["viewportWidth"] + overflow_tolerance
        ), (
            f"{page_name} has horizontal document overflow: {layout}"
        )
        assert layout["bodyWidth"] <= (
            layout["viewportWidth"] + overflow_tolerance
        ), (
            f"{page_name} has horizontal body overflow: {layout}"
        )
        assert elements.count() > 0, f"{page_name} has no usable controls"
        for index in range(elements.count()):
            element = elements.nth(index)
            element.scroll_into_view_if_needed()
            box = element.bounding_box()
            assert box and box["width"] > 0 and box["height"] > 0, (
                f"{page_name} control {index + 1} has no usable size"
            )
            assert box["x"] >= -overflow_tolerance, (
                f"{page_name} control {index + 1} is clipped on the left: {box}"
            )
            assert box["x"] + box["width"] <= (
                layout["viewportWidth"] + overflow_tolerance
            ), (
                f"{page_name} control {index + 1} is clipped on the right: {box}"
            )
        return layout

    def open_non_member_payment_page(self):
        buttons = self._join_buttons()
        assert buttons.count() == 3, (
            f"Non-Pro user should see 3 Join buttons, found {buttons.count()}"
        )
        buttons.first.click()
        self.page.wait_for_url(
            "**/sat-pro-payment",
            wait_until="domcontentloaded",
        )
        assert self._path() == self.PAYMENT_PATH

    def verify_payment_page_and_safe_popups(self):
        self.page.get_by_role(
            "heading",
            name="Payment Details",
            exact=True,
        ).wait_for(state="visible")
        assert self.page.get_by_text(
            "Enter the following details to subscribe to SAT Pro",
            exact=True,
        ).is_visible()
        assert self._normalized_text(
            self.page.locator("h3.user-profile-title")
        ) == "USM USER QA USER"
        assert self._normalized_text(
            self.page.locator("p.user-profile-email")
        ) == "usmanqaengineer@gmail.com"
        assert self._normalized_text(
            self.page.locator("span.badge.bg-blue-50")
        ) == "Master Level 3"
        assert self.page.get_by_role(
            "heading",
            name="Become a PRO and Start Saving Today",
            exact=True,
        ).is_visible()

        # The PayPal iframe becomes visible before its popup click handlers
        # finish initializing on Development.
        self.page.wait_for_timeout(3000)
        for payment_method in ("PayPal", "Debit or Credit Card"):
            paypal_frame = self.page.frame_locator(
                "iframe[title='PayPal']:visible"
            ).first
            method = paypal_frame.get_by_role(
                "link",
                name=payment_method,
                exact=True,
            )
            method.wait_for(state="visible", timeout=30000)
            with self.page.context.expect_page(timeout=30000) as popup_info:
                method.click()
            popup = popup_info.value
            try:
                assert not popup.is_closed(), (
                    f"{payment_method} did not open a payment popup"
                )
                assert "PayPal" in popup.title(), (
                    f"Unexpected {payment_method} popup title: {popup.title()}"
                )
            finally:
                if not popup.is_closed():
                    popup.close()
            self.page.wait_for_timeout(1000)
            assert self._path() == self.PAYMENT_PATH

    def verify_mobile_payment_page_controls(self):
        self.page.get_by_role(
            "heading",
            name="Payment Details",
            exact=True,
        ).wait_for(state="visible")
        assert self._path() == self.PAYMENT_PATH
        assert self.page.get_by_text(
            "Enter the following details to subscribe to SAT Pro",
            exact=True,
        ).is_visible()

        iframe = self.page.locator("iframe[title='PayPal']:visible").first
        iframe.wait_for(state="visible", timeout=30000)
        self._verify_mobile_layout(
            "SAT Pro payment page",
            self.page.locator(
                "h3.user-profile-title:visible, "
                "span.badge.bg-blue-50:visible, "
                "iframe[title='PayPal']:visible"
            ),
        )

        payment_frame = self.page.frame_locator(
            "iframe[title='PayPal']:visible"
        ).first
        for payment_method in ("PayPal", "Debit or Credit Card"):
            control = payment_frame.get_by_role(
                "link",
                name=payment_method,
                exact=True,
            )
            control.wait_for(state="visible", timeout=30000)
            assert control.is_enabled(), (
                f"{payment_method} is disabled on the mobile payment page"
            )
        assert self._path() == self.PAYMENT_PATH

    def verify_active_member_and_membership_page(self):
        heading = self.page.locator("h1:visible,h2:visible").filter(
            has_text="You're a SAT Pro!"
        ).first
        heading.wait_for(state="visible")
        assert self._normalized_text(heading) == "You're a SAT Pro!"

        place_orders = self.page.get_by_role(
            "link",
            name="Place an Order",
            exact=True,
        ).filter(visible=True)
        assert place_orders.count() == 2, (
            f"Expected 2 Place an Order CTAs, found {place_orders.count()}"
        )
        for index in range(place_orders.count()):
            assert urlparse(
                place_orders.nth(index).get_attribute("href")
            ).path == "/used-cars"

        manage = self.page.get_by_role(
            "link",
            name="Manage membership",
            exact=True,
        )
        assert urlparse(manage.get_attribute("href")).path == self.MEMBERSHIP_PATH
        manage.click()
        self.page.wait_for_url(
            "**/sat-pro-membership",
            wait_until="domcontentloaded",
        )
        assert self._path() == self.MEMBERSHIP_PATH

        for title in ("Your Membership", "Manage Subscription", "You're a SAT Pro!"):
            assert self.page.get_by_role(
                "heading",
                name=title,
                exact=True,
            ).filter(visible=True).count() == 1, (
                f"Membership heading is missing: {title}"
            )

        membership_order = self.page.get_by_role(
            "link",
            name="Place an Order",
            exact=True,
        ).filter(visible=True)
        assert membership_order.count() == 1
        assert urlparse(membership_order.get_attribute("href")).path == "/used-cars"

        end_membership = self.page.locator(".drp-sat-memeber-end")
        assert end_membership.get_attribute("aria-expanded") == "false"
        end_membership.click()
        panel = self.page.locator("#collapseSatmemberEnd")
        panel.wait_for(state="visible")
        assert end_membership.get_attribute("aria-expanded") == "true"
        panel_text = self._normalized_text(panel)
        for reason in self.CANCELLATION_REASONS:
            assert reason in panel_text, f"Cancellation reason is missing: {reason}"
        assert panel.locator("input[name='reason']").count() == 5
        submit = panel.get_by_role("button", name="Submit", exact=True)
        assert submit.is_visible(), "End Membership Submit button is missing"
        assert self._path() == self.MEMBERSHIP_PATH

    def verify_mobile_active_member_and_membership_page(self):
        self._verify_mobile_layout(
            "Active SAT Pro landing page",
            self.page.get_by_role(
                "link",
                name="Place an Order",
                exact=True,
            ).filter(visible=True).or_(
                self.page.get_by_role(
                    "link",
                    name="Manage membership",
                    exact=True,
                ).filter(visible=True)
            ),
        )
        self.verify_active_member_and_membership_page()
        self._verify_mobile_layout(
            "SAT Pro membership page",
            self.page.locator(
                ".drp-sat-memeber-end:visible, "
                "#collapseSatmemberEnd input[name='reason']:visible, "
                "#collapseSatmemberEnd button:visible"
            ),
        )
        assert self._path() == self.MEMBERSHIP_PATH
