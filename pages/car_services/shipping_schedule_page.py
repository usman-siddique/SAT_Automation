"""Page object for the Shipping Schedule service."""

from urllib.parse import parse_qs, urlparse

from playwright.sync_api import TimeoutError as PlaywrightTimeoutError


class ShippingSchedulePage:
    REQUIRED_CARD_FIELDS = (
        "Ship Name",
        "Company Name",
        "Voyage No",
        "Departure Port",
        "Departure Date",
        "Due Date",
    )

    def __init__(self, page):
        self.page = page

    def verify_page_contract(self):
        self.page.wait_for_url("**/shipping-schedule*")
        heading = self.page.locator("h1.title-page").first
        heading.wait_for(state="visible")
        intro = self.page.locator("p.see-first-para")
        intro.wait_for(state="visible")

        controls = (
            "#select2-departure_port-container",
            "#select2-region-container",
            "#select2-arrival_port-container",
            "#select2-ship_name-container",
            ".departure_date_from",
            ".departure_date_to",
            ".arrival_date_from",
            ".arrival_date_to",
            ".btn-search-filter",
            ".btn-reset-filter",
        )
        for selector in controls:
            self.page.locator(selector).wait_for(state="visible")

        return {
            "path": urlparse(self.page.url).path,
            "heading": heading.inner_text().strip(),
            "intro_present": bool(intro.inner_text().strip()),
            "controls_visible": True,
        }

    def verify_mobile_page_contract(self):
        self.page.wait_for_url("**/shipping-schedule*")
        heading = self.page.locator("h1.title-page").first
        heading.wait_for(state="visible")
        required_controls = {
            "departure port": "#select2-departure_port-container",
            "region": "#select2-region-container",
            "arrival port": "#select2-arrival_port-container",
            "ship name": "#select2-ship_name-container",
            "departure from": ".departure_date_from",
            "departure to": ".departure_date_to",
            "arrival from": ".arrival_date_from",
            "arrival to": ".arrival_date_to",
            "search": ".btn-search-filter",
            "reset": ".btn-reset-filter",
        }
        missing = [
            label
            for label, selector in required_controls.items()
            if not self.page.locator(selector).is_visible()
        ]
        assert not missing, (
            "Mobile Shipping Schedule hides required filters/actions: "
            + ", ".join(missing)
        )
        return {
            "path": urlparse(self.page.url).path,
            "heading": heading.inner_text().strip(),
            "controls_visible": True,
        }

    def get_filter_options(self, select_id):
        return [
            text.strip()
            for text in self.page.locator(
                f"#{select_id} option"
            ).all_inner_texts()
            if text.strip() and text.strip().lower() != "select"
        ]

    def get_schedules(self):
        cards = self.page.locator(".filter-data-card")
        schedules = []
        for index in range(cards.count()):
            card = cards.nth(index)
            fields = card.locator("td").evaluate_all(
                """cells => Object.fromEntries(cells.map(cell => {
                    const label = cell.querySelector('.title-filterdata');
                    const value = cell.querySelector('.data-filter');
                    return label && value
                        ? [label.textContent.trim(), value.textContent.trim()]
                        : null;
                }).filter(Boolean))"""
            )
            arrivals = card.locator(
                ".list-data-table tbody tr"
            ).evaluate_all(
                """rows => rows.map(row => {
                    const values = [...row.querySelectorAll('td')]
                        .map(cell => cell.textContent.trim());
                    return {port: values[0], eta: values[1]};
                })"""
            )
            schedules.append({"fields": fields, "arrivals": arrivals})
        return schedules

    def verify_initial_schedule_data(self):
        schedules = self.get_schedules()
        assert schedules, "No shipping schedules are displayed."
        for field in self.REQUIRED_CARD_FIELDS:
            assert schedules[0]["fields"].get(field), (
                f"The first schedule is missing {field}."
            )
        assert schedules[0]["arrivals"], (
            "The first schedule has no Arrival Port / ETA details."
        )
        assert all(
            arrival["port"] and arrival["eta"]
            for arrival in schedules[0]["arrivals"]
        )
        return schedules

    def expand_first_schedule(self):
        card = self.page.locator(".filter-data-card").first
        expand = card.locator(".expand")
        target_id = expand.get_attribute("aria-label-id")
        assert target_id, "First schedule has no expandable-details target."
        expand.click()
        details = self.page.locator(f"#{target_id}")
        details.wait_for(state="visible")
        headers = [
            text.strip()
            for text in details.locator("thead td").all_inner_texts()
        ]
        assert headers == ["Arrival Port", "ETA"]
        return details.locator("tbody tr").count()

    def find_region_for_arrival(self, arrival_port):
        for region in self.get_filter_options("region"):
            self.page.locator("#region").select_option(label=region)
            try:
                self.page.wait_for_function(
                    """port => [...document.querySelectorAll(
                        '#arrival_port option'
                    )].some(option => option.textContent.trim() === port)""",
                    arg=arrival_port,
                    timeout=3000,
                )
                return region
            except PlaywrightTimeoutError:
                continue
        raise AssertionError(
            f"No Region loaded the live arrival port {arrival_port!r}."
        )

    def select_filters(self, departure, region, arrival, ship):
        self.page.locator("#region").select_option(label=region)
        self.page.wait_for_function(
            """port => [...document.querySelectorAll(
                '#arrival_port option'
            )].some(option => option.textContent.trim() === port)""",
            arg=arrival,
            timeout=10000,
        )
        self.page.locator("#departure_port").select_option(label=departure)
        self.page.locator("#arrival_port").select_option(label=arrival)
        self.page.locator("#ship_name").select_option(label=ship)

    def search(self):
        with self.page.expect_navigation(wait_until="domcontentloaded"):
            self.page.locator(".btn-search-filter").click()
        self.page.wait_for_function(
            """() => document.querySelector('.filter-data-card')
                || document.querySelector('h2.not-found-text')"""
        )
        query = parse_qs(urlparse(self.page.url).query)
        return {key: values[0] for key, values in query.items()}

    def reset(self):
        with self.page.expect_navigation(wait_until="domcontentloaded"):
            self.page.locator(".btn-reset-filter").click()
        self.page.wait_for_url("**/shipping-schedule")
        assert not urlparse(self.page.url).query
        assert self.page.locator(".filter-data-card").count() > 0

    def verify_results_match(self, departure, arrival, ship):
        schedules = self.get_schedules()
        assert schedules, "Valid shipping filters returned no schedules."
        assert all(
            schedule["fields"]["Departure Port"] == departure
            and schedule["fields"]["Ship Name"] == ship
            and any(
                item["port"] == arrival
                for item in schedule["arrivals"]
            )
            for schedule in schedules
        ), "Filtered shipping results do not match all selected values."
        return len(schedules)

    def verify_no_results(self):
        message = self.page.locator("h2.not-found-text")
        message.wait_for(state="visible")
        assert message.inner_text().strip()
        assert self.page.locator(".filter-data-card").count() == 0
        return message.inner_text().strip()

    def choose_date(self, selector, day):
        field = self.page.locator(selector)
        field.click()
        calendar = self.page.locator(".container__main:visible")
        calendar.wait_for(state="visible")
        calendar.locator(f".day-item:text-is('{day}')").first.click()
        value = field.input_value().strip()
        assert value, f"Date picker {selector} did not populate its field."
        return value

    def verify_shipping_notes(self):
        link = self.page.locator("a[href='#shipping_note']")
        link.wait_for(state="visible")
        link.click()
        notes = self.page.locator("#shipping_note")
        notes.wait_for(state="visible")
        text = notes.inner_text()
        required_notes = (
            "cut-off date",
            "shipping schedules can change",
            "Port of Departure",
            "delaying your departure",
            "Space availability",
            "does not guarantee a shipment",
        )
        assert all(note.lower() in text.lower() for note in required_notes)
        return len(required_notes)
