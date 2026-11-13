"""Page object for the SAT vehicle Storage Service."""

from urllib.parse import urlparse


class StorageServicePage:
    COUNTRIES = [
        "Japan",
        "Kenya",
        "Tanzania",
        "South Africa",
        "Mozambique",
        "Europe",
        "South America",
        "Uganda",
    ]

    BENEFITS = [
        "Maximum Security",
        "Peace of Mind",
        "Customized Care",
        "Reduced risk of damage",
    ]

    USE_CASES = [
        "You are on vacation and need a safe place to store your vehicle",
        (
            "You haven't sold your previous car and need storage space "
            "until you sell it"
        ),
        (
            "You want to preserve your vehicle until you are ready to "
            "embrace it fully"
        ),
    ]

    def __init__(self, page):
        self.page = page

    @staticmethod
    def _clean(text):
        return " ".join(text.split())

    def verify_overview(self):
        heading = self.page.get_by_role(
            "heading",
            name="Secure Storage Service For Your Vehicle's Safety",
            exact=True,
        )
        heading.wait_for(state="visible")
        overview = self.page.get_by_role(
            "heading", name="Overview", exact=True
        )
        overview.scroll_into_view_if_needed()

        body_text = self._clean(self.page.locator("body").inner_text())
        required_policy_points = (
            "climate-controlled and safe environment",
            "free of cost for the first 30 days",
            "storage period starts from the date you place an order",
            "all the shipments are managed at the earliest convenience",
            "export customs custody after booking shipment cannot be availed",
            "want to delay their shipment",
            "contact our sales manager",
        )
        assert all(
            point.lower() in body_text.lower()
            for point in required_policy_points
        )
        return {
            "path": urlparse(self.page.url).path,
            "heading": heading.inner_text().strip(),
            "policy_points": len(required_policy_points),
        }

    def get_storage_fees(self):
        table = self.page.locator("table").first
        table.scroll_into_view_if_needed()
        headers = [
            self._clean(text)
            for text in table.locator("thead th").all_inner_texts()
        ]
        assert headers == [
            "Storage Fee Charged Per Vehicle",
            "1-30 days",
            "31-60 days",
            "61-90 days",
        ]

        records = []
        rows = table.locator("tbody tr")
        for index in range(rows.count()):
            cells = rows.nth(index).locator("td")
            assert cells.count() == 4
            first_period = self._clean(cells.nth(1).inner_text())
            first_period_icon = cells.nth(1).locator("img.check-icon")
            icon_loaded = False
            if first_period_icon.count():
                icon_loaded = first_period_icon.evaluate(
                    "image => image.complete && image.naturalWidth > 0"
                )
            records.append(
                {
                    "country": self._clean(cells.nth(0).inner_text()),
                    "days_1_30": first_period,
                    "days_1_30_icon": icon_loaded,
                    "days_31_60": self._clean(cells.nth(2).inner_text()),
                    "days_61_90": self._clean(cells.nth(3).inner_text()),
                }
            )
        return records

    def verify_benefits(self):
        heading = self.page.get_by_role(
            "heading",
            name="Benefits of SAT Vehicle Storage Service",
            exact=True,
        )
        heading.scroll_into_view_if_needed()
        cards = self.page.locator(".vehicle-strorage-crd")
        texts = [
            self._clean(text)
            for text in cards.locator(
                ".benefit-vechicle-hdr"
            ).all_inner_texts()
        ]
        assert texts == self.BENEFITS
        assert all(
            cards.nth(index).locator("img").evaluate(
                "image => image.complete && image.naturalWidth > 0"
            )
            for index in range(cards.count())
        ), "One or more Storage benefit icons failed to load."
        return texts

    def verify_use_cases(self):
        heading = self.page.get_by_role(
            "heading", name="Why Store a New Vehicle?", exact=True
        )
        heading.scroll_into_view_if_needed()
        cards = self.page.locator(".new-vehicle-card-main")
        texts = [
            self._clean(text)
            for text in cards.locator(
                ".stgr-botm-img-hdr"
            ).all_inner_texts()
        ]
        assert texts == self.USE_CASES
        assert all(
            cards.nth(index).locator("img").evaluate(
                "image => image.complete && image.naturalWidth > 0"
            )
            for index in range(cards.count())
        ), "One or more Storage use-case images failed to load."
        return texts
