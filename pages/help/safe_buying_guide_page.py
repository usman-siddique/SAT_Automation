class SafeBuyingGuidePage:
    FRAUD_GUIDANCE = (
        "Do Not Pay Before Investigating",
        "Keep Your Vehicle Safe From Buyers",
        "Cyber Safety Precaution",
        "Vehicular Investigation Scam",
    )
    TAB_TARGETS = {
        "Buying Check-List": "#my-reviews",
        "Online Safety": "#add-review",
    }
    BUYING_CHECKS = (
        "Documents",
        "Vehicular History Reports",
        "Price Comparison",
        "Test Drive",
        "Go Cashless",
        "Insurance Is a Must",
    )
    ONLINE_SAFETY_CHECKS = (
        "Protect Your Device",
        "Set Strong Passwords",
        "Avoid Phishing",
        "Stay Cautious When Entering Bank Details",
    )
    VEHICLE_CHECKS = (
        "Vehicle Security",
        "Fraud Protection",
        "History Report",
    )

    def __init__(self, page):
        self.page = page

    def get_banner(self):
        banner = self.page.locator(".swb")
        return {
            "title": " ".join(
                banner.locator(".swb__title").inner_text().split()
            ),
            "image_alt": banner.locator(".swb__bg").get_attribute("alt"),
        }

    def get_main_section_content(self):
        main = self.page.locator(".safety-with-sat-mian")
        return {
            "detail": main.get_by_text("Detail", exact=True).inner_text(),
            "fraud_heading": main.get_by_text(
                "How to Beware Of Fraudulent Activities", exact=True
            ).inner_text(),
            "fraud_guidance": [
                main.get_by_text(name, exact=True).inner_text().strip()
                for name in self.FRAUD_GUIDANCE
            ],
            "safe_heading": main.get_by_text(
                "Staying Safe the SAT Way", exact=True
            ).inner_text(),
        }

    def get_tabs(self):
        tabs = self.page.locator(".tab-nav-link-ul [role='tab']")
        return [
            {
                "label": " ".join(tabs.nth(index).inner_text().split()),
                "target": tabs.nth(index).get_attribute("href"),
                "selected": tabs.nth(index).get_attribute("aria-selected"),
            }
            for index in range(tabs.count())
        ]

    def select_tab(self, label):
        target = self.TAB_TARGETS[label]
        tab = self.page.locator(f"a[href='{target}']")
        tab.click()
        self.page.wait_for_function(
            """target => {
                const panel = document.querySelector(target);
                return panel && panel.classList.contains('active') &&
                    panel.classList.contains('show');
            }""",
            arg=target,
        )
        panel = self.page.locator(target)
        return {
            "selected": tab.get_attribute("aria-selected"),
            "active": "active" in (tab.get_attribute("class") or ""),
            "panel_visible": panel.is_visible(),
            "headings": [
                text.strip()
                for text in panel.locator(
                    ".safety-common-sub-hdr"
                ).all_inner_texts()
            ],
            "descriptions": [
                text.strip()
                for text in panel.locator(
                    ".safety-common-paragraph"
                ).all_inner_texts()
            ],
        }

    def get_vehicle_checks(self):
        section = self.page.locator("section.rating-sction")
        return {
            "heading": section.get_by_role(
                "heading", name="What Our Vehicle Checks Offer", exact=True
            ).inner_text().strip(),
            "cards": [
                text.strip()
                for text in section.locator(".offer-hdr").all_inner_texts()
            ],
            "descriptions": [
                text.strip()
                for text in section.locator(".offer-para").all_inner_texts()
            ],
        }

    def get_image_status(self):
        images = self.page.locator(".swb__bg, section.rating-sction .rating-icon")
        return [
            images.nth(index).evaluate(
                """image => ({
                    loaded: image.complete && image.naturalWidth > 0,
                    src: image.currentSrc || image.src,
                })"""
            )
            for index in range(images.count())
        ]
