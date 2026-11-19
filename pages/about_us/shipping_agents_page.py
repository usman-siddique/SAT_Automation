import re
from urllib.parse import urlparse


class ShippingAgentsPage:
    PATH = "/shipping-agents"
    COUNTRIES = (
        "Bangladesh",
        "Cameroon",
        "Gambia",
        "Kazakhstan",
        "Sri Lanka",
        "Trinidad and Tobago",
    )

    def __init__(self, page):
        self.page = page

    def _network(self):
        return self.page.get_by_role(
            "heading", name="Our Global Network", exact=True
        ).locator("xpath=ancestor::div[contains(@class, 'container')][1]")

    def _visible_filter(self):
        return self._network().locator("button.satSelectBtn:visible")

    def _visible_cards(self):
        return self._network().locator(".country-list-agents:visible")

    def _navigate_mobile_path(self):
        self.page.locator(
            "#menu_logo_mobile span[data-bs-target='#sidebarmobile']"
        ).click()
        self.page.locator("#sidebarmobile a.main-items-sidebar-content").filter(
            has_text="About Us"
        ).click()
        link = self.page.locator(
            "#offcanvascaroverview a[href$='/shipping-agents']"
        )
        link.wait_for(state="visible")
        link.click()

    def go_to_shipping_agents(self):
        menu = self.page.locator("p.cnm-cls:has-text('About Us')").locator("..")
        menu.hover()
        link = menu.locator(".dropdown_content_header").get_by_role(
            "link", name="Shipping Agents", exact=True
        )
        link.wait_for(state="visible")
        link.click()
        self._wait_until_ready()

    def go_to_shipping_agents_mobile(self):
        self._navigate_mobile_path()
        self._wait_until_ready()
        assert self.page.locator("#navbar_mobile_header").is_visible(), (
            "Shipping Agents mobile header is not visible"
        )

    def _wait_until_ready(self):
        self.page.wait_for_url("**/shipping-agents", wait_until="domcontentloaded")
        self.page.get_by_role(
            "heading", name="Explore Our International Office Map", exact=True
        ).wait_for(state="visible")
        self.page.get_by_role(
            "heading", name="Our Global Network", exact=True
        ).wait_for(state="visible")
        assert urlparse(self.page.url).path.rstrip("/") == self.PATH

    @staticmethod
    def _card_lines(card):
        return [line.strip() for line in card.inner_text().splitlines() if line.strip()]

    def _assert_card_data(self, card, expected_country=None):
        lines = self._card_lines(card)
        assert len(lines) >= 5, f"Shipping agent card has missing details: {lines}"
        title, country, email, phone = lines[:4]
        address = " ".join(lines[4:])
        assert title, "Shipping agent name is missing"
        if expected_country:
            assert country == expected_country, (
                f"{expected_country} filter returned a {country} agent"
            )
        else:
            assert country in self.COUNTRIES, (
                f"Unexpected shipping agent country: {country}"
            )
        assert re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email), (
            f"Shipping agent email is invalid: {email}"
        )
        assert len(re.sub(r"\D", "", phone)) >= 8, (
            f"Shipping agent phone is invalid: {phone}"
        )
        assert address, f"Shipping agent address is missing for {country}"

    def _select_country(self, country):
        button = self._visible_filter()
        assert button.count() == 1, "Visible Shipping Agents country filter is missing"
        button.click()
        option = self._network().locator("li.country-item:visible").filter(
            has_text=country
        )
        assert option.count() == 1, f"Shipping Agents filter is missing: {country}"
        option.click()
        assert button.inner_text().strip() == country
        expected_count = len(self.COUNTRIES) if country == "All" else 1
        self.page.wait_for_function(
            """({country, expectedCount}) => {
                const cards = [...document.querySelectorAll('.country-list-agents')]
                    .filter(card => card.getClientRects().length > 0);
                if (cards.length !== expectedCount) return false;
                if (country === 'All') return true;
                return cards.every(card => card.innerText
                    .split(String.fromCharCode(10))
                    .map(line => line.trim())
                    .filter(Boolean)[1] === country);
            }""",
            arg={"country": country, "expectedCount": expected_count},
        )

    def _assert_images_loaded(self, card):
        images = card.locator("img")
        assert images.count() == 5, (
            f"Shipping agent card media is incomplete: {self._card_lines(card)}"
        )
        card.scroll_into_view_if_needed()
        for _ in range(40):
            unloaded = images.evaluate_all(
                "imgs => imgs.filter(img => !img.complete || img.naturalWidth === 0)"
                ".map(img => img.src)"
            )
            if not unloaded:
                return
            self.page.wait_for_timeout(250)
        assert not unloaded, f"Shipping agent card has unloaded images: {unloaded}"

    def verify_content_cards_and_media(self):
        assert self.page.title() == (
            "Shipping Agents | Leading Used Car Exporter | SAT Japan"
        )
        intro = self.page.locator("section.container .para-shipagent:visible")
        assert intro.count() == 1, "Shipping Agents introduction is missing"
        assert len(" ".join(intro.inner_text().split())) > 40, (
            "Shipping Agents introduction is incomplete"
        )

        map_image = self.page.locator("img[alt='sat agent map']:visible")
        assert map_image.count() == 1, "Shipping Agents global map is missing"
        assert map_image.evaluate(
            "image => image.complete && image.naturalWidth > 0"
        ), "Shipping Agents global map did not load"

        network = self._network()
        options = network.locator("li.country-item").evaluate_all(
            "items => [...new Set(items.map(item => item.dataset.text))]"
        )
        assert options == ["All", *self.COUNTRIES], (
            f"Shipping Agents country options changed: {options}"
        )

        cards = self._visible_cards()
        assert cards.count() == len(self.COUNTRIES), (
            f"Expected {len(self.COUNTRIES)} shipping agents, found {cards.count()}"
        )
        for index in range(cards.count()):
            card = cards.nth(index)
            self._assert_card_data(card)
            self._assert_images_loaded(card)

        assert network.locator("a").count() == 0, (
            "Shipping Agents now contains page-specific links that need link checks"
        )

    def verify_every_country_filter_and_reset(self):
        initial_count = self._visible_cards().count()
        assert initial_count == len(self.COUNTRIES)
        for country in self.COUNTRIES:
            self._select_country(country)
            cards = self._visible_cards()
            assert cards.count() > 0, f"{country} filter returned no shipping agent"
            for index in range(cards.count()):
                self._assert_card_data(cards.nth(index), expected_country=country)

        self._select_country("All")
        assert self._visible_cards().count() == initial_count, (
            "All filter did not restore every shipping agent"
        )

    def verify_mobile_filter_and_layout(self):
        assert self.page.locator("#navbar_mobile_header").is_visible()
        assert self.page.locator("img[alt='sat agent map']:visible").is_visible()
        self._select_country("Sri Lanka")
        cards = self._visible_cards()
        assert cards.count() == 1, (
            f"Mobile Sri Lanka filter returned {cards.count()} cards"
        )
        self._assert_card_data(cards.first, expected_country="Sri Lanka")

        viewport = self.page.evaluate(
            "() => ({screen: screen.width, visual: visualViewport.width})"
        )
        assert 0 < viewport["visual"] <= viewport["screen"], (
            f"Shipping Agents device viewport is invalid: {viewport}"
        )
        elements = [
            self.page.locator("img[alt='sat agent map']:visible"),
            self._visible_filter(),
            cards.first,
        ]
        for element in elements:
            box = element.bounding_box()
            assert box and box["width"] > 0 and box["height"] > 0, (
                "Shipping Agents mobile content has no usable layout box"
            )

        self._select_country("All")
        assert self._visible_cards().count() == len(self.COUNTRIES), (
            "Mobile All filter did not restore every shipping agent"
        )
