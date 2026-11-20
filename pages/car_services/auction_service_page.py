import re
from decimal import Decimal
from pathlib import Path
from urllib.parse import urlparse

from playwright.sync_api import TimeoutError as PlaywrightTimeoutError


class AuctionServicePage:
    BIDDING_QUESTIONS = (
        "What is a “Bid Price”?",
        "What is the advanced deposit for?",
        "Can the advanced deposit be refunded?",
        "What is the deadline for placing bids?",
        "Can I place bids on multiple vehicles when I want to buy one?",
        "What is the deadline of payment after winning a bid?",
        "Can I cancel a purchase after winning the bid?",
    )
    COST_AND_SHIPPING_QUESTIONS = (
        "What are the total costs for purchasing through bidding services?",
        "What does the “Auction Service Fee” include and how much does it cost?",
        "Can I get the insurance service for an auction vehicle?",
        (
            "Can you place autoparts inside my purchased vehicle and ship "
            "them at the same time?"
        ),
    )
    FAQ_TABS = {
        "Bidding and Auction": "#v_pills_bidding",
        "Costs and Shipping": "#v_pills_shipping",
    }

    def __init__(self, page):
        self.page = page

    @staticmethod
    def _money(value, optional=False):
        cleaned = re.sub(r"[^0-9.-]", "", value or "")
        if not cleaned:
            if optional:
                return None
            raise AssertionError(f"Expected a money value, received {value!r}.")
        return Decimal(cleaned)

    def get_overview(self):
        overview = self.page.locator(".auction-service-overview")
        links = {
            "start_bidding": overview.locator(
                "a[href$='/used-cars/auction_cars']"
            ).get_attribute("href"),
            "calculator": overview.locator(
                "a[href$='/auction-calculator']"
            ).get_attribute("href"),
            "sheet_guide": overview.locator(
                "a[href$='/pdfs/Auction_Sheet_Guide.pdf']"
            ).get_attribute("href"),
            "house_map": overview.locator(
                "a[href$='/pdfs/auctions_map_house.pdf']"
            ).get_attribute("href"),
        }
        return {
            "heading": overview.locator("h3.title").inner_text().strip(),
            "description": overview.locator("p.para").inner_text().strip(),
            "links": links,
        }

    def download_overview_pdf(self, filename):
        link = self.page.locator(f"a[href$='/pdfs/{filename}']")
        with self.page.expect_download() as download_info:
            link.click()
        download = download_info.value
        path = Path(download.path())
        return {
            "filename": download.suggested_filename,
            "failure": download.failure(),
            "size": path.stat().st_size,
            "header": path.read_bytes()[:5],
        }

    def get_faq_tabs(self):
        tabs = self.page.locator("#v_pills_tabs [role='tab']")
        return [
            {
                "label": " ".join(tabs.nth(index).inner_text().split()),
                "target": tabs.nth(index).get_attribute("data-bs-target"),
                "selected": tabs.nth(index).get_attribute("aria-selected"),
            }
            for index in range(tabs.count())
        ]

    def select_faq_tab_and_expand_all(self, label):
        target = self.FAQ_TABS[label]
        tab = self.page.locator(
            f"#v_pills_tabs [data-bs-target='{target}']"
        )
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
        question_buttons = panel.locator(
            "button[data-bs-toggle='collapse']"
        )
        questions = []
        answers = []
        for index in range(question_buttons.count()):
            question = question_buttons.nth(index)
            questions.append(" ".join(question.inner_text().split()))
            answer_target = question.get_attribute("data-bs-target")
            if not answer_target:
                raise AssertionError("Auction FAQ has no answer target.")
            question.click()
            answer = self.page.locator(answer_target)
            answer.wait_for(state="visible")
            answers.append(" ".join(answer.inner_text().split()))

        return {
            "selected": tab.get_attribute("aria-selected"),
            "questions": questions,
            "answers": answers,
        }

    def open_start_bidding(self):
        self.page.locator(
            ".auction-service-overview "
            "a[href$='/used-cars/auction_cars']"
        ).click()
        self.page.wait_for_url("**/used-cars/auction_cars**")
        auction_tab = self.page.locator("#nav-auction-tab.active")
        auction_tab.wait_for(state="visible")
        return {
            "path": urlparse(self.page.url).path,
            "auction_tab_active": auction_tab.is_visible(),
        }

    def return_to_auction_service(self):
        parsed = urlparse(self.page.url)
        self.page.goto(
            f"{parsed.scheme}://{parsed.netloc}/sat-auction",
            wait_until="domcontentloaded",
        )
        self.page.locator(".auction-service-overview").wait_for(
            state="visible"
        )

    def open_cost_calculator(self):
        self.page.locator(
            ".auction-service-overview a[href$='/auction-calculator']"
        ).click()
        self.page.wait_for_url("**/auction-calculator")
        heading = self.page.get_by_role(
            "heading", name="Auction Cost Calculator", exact=True
        )
        heading.wait_for(state="visible")
        return {
            "path": urlparse(self.page.url).path,
            "heading": heading.inner_text().strip(),
        }

    def _select_destination(self, block_id, item_class, value):
        block = self.page.locator(f"#{block_id}")
        current = block.locator(".button-text").inner_text().strip()
        if current == value:
            return

        block.locator("button.satSelectBtn").click()
        item = block.locator(f"li.{item_class}", has_text=value)
        item.first.wait_for(state="visible")
        item.first.click()

    def load_stock_data(self, stock_id, country, port):
        if not stock_id:
            raise AssertionError(
                "Auction Calculator stock ID is missing. Add the current "
                "value to data/stock_ids.py."
            )

        stock_input = self.page.locator("#stock_id")
        stock_input.fill(stock_id.strip())

        try:
            outcome = self.page.wait_for_function(
                """() => {
                    const visibleText = Array.from(
                        document.querySelectorAll('body *')
                    ).find(element => {
                        const text = (element.textContent || '').trim();
                        const style = window.getComputedStyle(element);
                        return text === 'Auction car not found' &&
                            style.display !== 'none' &&
                            style.visibility !== 'hidden';
                    });
                    if (visibleText) return 'not_found';

                    const value = selector =>
                        (document.querySelector(selector)?.value || '').trim();
                    const text = selector =>
                        (document.querySelector(selector)?.textContent || '')
                            .trim();
                    const ready = value('#car_id') && value('#bidInput') &&
                        value('#m3');
                    return ready ? 'available' : false;
                }""",
                timeout=25000,
            ).json_value()
        except PlaywrightTimeoutError as error:
            raise AssertionError(
                f"Auction stock {stock_id} did not finish loading its vehicle "
                "and cost data within 25 seconds."
            ) from error

        if outcome == "not_found":
            raise AssertionError(
                f"Auction stock {stock_id} is no longer available. Replace "
                "the auction_calculator value in data/stock_ids.py."
            )

        self._select_destination(
            "destination_country_block",
            "data-li-destination_country",
            country,
        )
        self.page.wait_for_timeout(800)
        self._select_destination(
            "destination_port_block",
            "data-li-destination_port",
            port,
        )

        try:
            self.page.wait_for_function(
                """expected => {
                    const text = selector =>
                        (document.querySelector(selector)?.textContent || '')
                            .trim();
                    const country = text(
                        '#destination_country_block .button-text'
                    );
                    const port = text('#destination_port_block .button-text');
                    return country === expected.country &&
                        port === expected.port &&
                        text('#agent_fee_dtl') &&
                        text('#inspection_fee_dtl') &&
                        text('#insurance_fee_dtl') &&
                        text('#shipping_fee_dtl') &&
                        Array.from(
                            document.querySelectorAll('.total_price_of_bid')
                        ).every(element => element.textContent.trim());
                }""",
                arg={"country": country, "port": port},
                timeout=25000,
            )
        except PlaywrightTimeoutError as error:
            raise AssertionError(
                f"Auction costs did not finish loading for {country} / "
                f"{port} within 25 seconds."
            ) from error

        agent_text = self.page.locator("#agent_fee_dtl").inner_text().strip()
        total_texts = [
            text.strip()
            for text in self.page.locator(
                ".total_price_of_bid"
            ).all_inner_texts()
            if text.strip()
        ]
        return {
            "stock_id": stock_input.input_value(),
            "car_id": self.page.locator("#car_id").input_value(),
            "bid_input": self._money(
                self.page.locator("#bidInput").input_value()
            ),
            "m3": Decimal(self.page.locator("#m3").input_value()),
            "deposit": self._money(
                self.page.locator(".deposit_deducted").inner_text()
            ),
            "country": self.page.locator(
                "#destination_country_block .button-text"
            ).inner_text().strip(),
            "port": self.page.locator(
                "#destination_port_block .button-text"
            ).inner_text().strip(),
            "bidding_amount": self._money(
                self.page.locator("#bidAmount").inner_text()
            ),
            "agent_fee": self._money(agent_text, optional=True),
            "agent_fee_text": agent_text,
            "inspection": self._money(
                self.page.locator("#inspection_fee_dtl").inner_text()
            ),
            "insurance": self._money(
                self.page.locator("#insurance_fee_dtl").inner_text()
            ),
            "shipping": self._money(
                self.page.locator("#shipping_fee_dtl").inner_text()
            ),
            "total": self._money(total_texts[0], optional=True),
            "displayed_totals": [
                self._money(text, optional=True) for text in total_texts
            ],
        }

    def _estimate_opens(self):
        try:
            with self.page.expect_popup(timeout=3000) as popup_info:
                self.page.locator("#downloadEstimate").click()
        except PlaywrightTimeoutError:
            return False

        popup = popup_info.value
        popup.close()
        return True

    def verify_unknown_stock_blocks_estimate(self, stock_id):
        stock_input = self.page.locator("#stock_id")
        stock_input.fill(stock_id)
        stock_input.dispatch_event("keyup")
        stock_input.dispatch_event("change")
        self.page.wait_for_function(
            """() => Array.from(document.querySelectorAll('body *')).some(
                element => element.textContent.trim() === 'Auction car not found' &&
                    getComputedStyle(element).display !== 'none' &&
                    getComputedStyle(element).visibility !== 'hidden'
            )""",
            timeout=25000,
        )
        message = self.page.get_by_text(
            "Auction car not found", exact=True
        ).filter(visible=True).first
        assert not self.page.locator("#car_id").input_value().strip()
        return {
            "message": message.inner_text().strip(),
            "estimate_generated": self._estimate_opens(),
        }

    def verify_missing_destinations_block_estimate(
        self,
        stock_id,
        country,
        port,
    ):
        self.load_stock_data(stock_id, country, port)
        country_value = self.page.locator("#destination_country_val")
        port_value = self.page.locator("#destination_port_val")
        original_country = country_value.input_value()
        original_port = port_value.input_value()
        assert original_country and original_port

        def set_hidden_value(locator, value):
            locator.evaluate(
                """(element, nextValue) => {
                    element.value = nextValue;
                    element.dispatchEvent(new Event('input', {bubbles: true}));
                    element.dispatchEvent(new Event('change', {bubbles: true}));
                }""",
                value,
            )

        results = {}
        try:
            set_hidden_value(country_value, "")
            results["missing_country"] = self._estimate_opens()

            set_hidden_value(country_value, original_country)
            set_hidden_value(port_value, "")
            results["missing_port"] = self._estimate_opens()
        finally:
            set_hidden_value(country_value, original_country)
            set_hidden_value(port_value, original_port)
        return results

    def verify_bid_boundaries(self, stock_id, country, port):
        data = self.load_stock_data(stock_id, country, port)
        bid = self.page.locator("#bidInput")
        original_bid = bid.input_value()
        invalid_results = {}

        try:
            for label, value in (
                ("empty", ""),
                ("zero", "0"),
                ("negative", "-1"),
            ):
                bid.fill(value)
                bid.dispatch_event("change")
                bid.blur()
                self.page.wait_for_timeout(300)
                invalid_results[label] = {
                    "estimate_generated": self._estimate_opens(),
                    "bid_amount": self.page.locator(
                        "#bidAmount"
                    ).inner_text().strip(),
                    "totals": self.page.locator(
                        ".total_price_of_bid"
                    ).all_inner_texts(),
                }

            bid.fill("1")
            bid.dispatch_event("change")
            bid.blur()
            self.page.wait_for_function(
                "() => document.querySelector('#bidAmount')?.textContent.trim() === '1'"
            )
            minimum_total = self._money(
                self.page.locator(".total_price_of_bid").first.inner_text(),
                optional=True,
            )
            minimum_result = {
                "bid_amount": self._money(
                    self.page.locator("#bidAmount").inner_text()
                ),
                "total": minimum_total,
                "estimate_generated": self._estimate_opens(),
            }
        finally:
            bid.fill(original_bid)
            bid.dispatch_event("change")

        return {
            "initial_bid": data["bid_input"],
            "invalid": invalid_results,
            "minimum": minimum_result,
        }

    @staticmethod
    def _display_money(amount):
        return f"${amount:,.0f}"

    def open_estimate(self, calculator_data):
        country = calculator_data["country"]
        with self.page.expect_popup() as popup_info:
            self.page.locator("#downloadEstimate").click()
        estimate = popup_info.value
        try:
            estimate.wait_for_url("**/download-estimate")
            heading = estimate.get_by_role(
                "heading",
                name=f"Auction Cost Calculator for {country}",
                exact=True,
            )
            heading.wait_for(state="visible")
            body_text = estimate.locator("body").inner_text()
            expected_amounts = [
                calculator_data["bidding_amount"],
                calculator_data["inspection"],
                calculator_data["insurance"],
                calculator_data["shipping"],
            ]
            if calculator_data["agent_fee"] is not None:
                expected_amounts.append(calculator_data["agent_fee"])
            if calculator_data["total"] is not None:
                expected_amounts.append(calculator_data["total"])

            pdf_button = estimate.get_by_role(
                "button", name="Download as PDF", exact=True
            )
            pdf_button.wait_for(state="visible")
            estimate.evaluate(
                """() => {
                    window.__satPrintCalled = false;
                    window.print = () => { window.__satPrintCalled = true; };
                }"""
            )
            pdf_button.click()
            pdf_action_working = estimate.evaluate(
                "() => window.__satPrintCalled"
            )

            return {
                "path": urlparse(estimate.url).path,
                "heading": heading.inner_text().strip(),
                "stock_id_visible": (
                    calculator_data["stock_id"].lower()
                    in body_text.lower()
                ),
                "cost_breakdown_visible": all(
                    label in body_text
                    for label in (
                        "Auction Cost Breakdown",
                        "Bidding Amount",
                        "Agent Fee",
                        "Inspection",
                        "Insurance",
                        "Shipping Cost",
                        "Total Payable",
                    )
                ),
                "amounts_visible": all(
                    self._display_money(amount) in body_text
                    for amount in expected_amounts
                ),
                "pdf_action_working": pdf_action_working,
            }
        finally:
            estimate.close()
