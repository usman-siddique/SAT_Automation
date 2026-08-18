from urllib.parse import urlparse

from playwright.sync_api import TimeoutError as PlaywrightTimeoutError


class HowToBuyPage:
    FAQ_CONTENT = (
        (
            "How can I buy a car directly from Japan?",
            "The car purchase process is in three easy steps. Firstly, use "
            "our search engine to find your desired car from our extensive "
            "inventory. Then click 'Buy Now' and fill in all the required "
            "information. Lastly, pay for your car with one of our secure "
            "payment methods and get your vehicle delivered in 4 to 8 weeks.",
        ),
        (
            "How do I find out the rules and regulations for importing a car "
            "to my country?",
            "To find out the import regulations in your country, please visit "
            "your local country page on our website or contact our support "
            "team at support@satjapan.co",
        ),
        (
            "Which payment methods are accepted by SAT?",
            "We accept payments through credit and debit cards, PayPal, and "
            "Telegraphic Transfer.",
        ),
        (
            "Can I get a discount on purchasing any vehicle?",
            "If you want a discount on the price of any vehicle, contact our "
            "sales team at sales@satjapan.co",
        ),
        (
            "Who should I consult if I have any questions?",
            "If you have more questions or queries, feel free to consult our "
            "customer support at support@satjapan.co. We will be happy to "
            "assist you.",
        ),
    )
    DEALER_STATE_HEADINGS = (
        "Create an Account",
        "Become a Dealer Today",
        "Your Dealer Account Was Rejected",
        "You Already Have a Dealer Account",
    )

    def __init__(self, page):
        self.page = page

    def get_main_heading(self):
        heading = self.page.get_by_role(
            "heading", name="How to Buy a Car with SAT", exact=True
        )
        heading.wait_for(state="visible")
        return heading.inner_text().strip()

    def get_purchase_steps(self):
        expected_steps = (
            "1. Search Vehicle",
            "2. Buy Now or Reserve",
            "3. Track Your Order",
            "4. Receive Delivery",
        )
        steps = []
        for name in expected_steps:
            heading = self.page.get_by_role("heading", name=name, exact=True)
            heading.wait_for(state="visible")
            steps.append(heading.inner_text().strip())
        return steps

    def get_faq_questions(self):
        faq_heading = self.page.get_by_role(
            "heading", name="Frequently Asked Questions", exact=True
        )
        faq_heading.wait_for(state="visible")
        return [
            text.strip()
            for text in self.page.locator(
                "button[data-bs-toggle='collapse']:visible"
            ).all_inner_texts()
            if text.strip()
        ]

    def get_faq_content(self):
        content = []
        questions = self.page.locator(
            "button[data-bs-toggle='collapse']:visible"
        )
        for index in range(questions.count()):
            question = questions.nth(index)
            target = question.get_attribute("data-bs-target")
            if not target:
                raise AssertionError("A How To Buy FAQ has no answer target.")
            question.click()
            answer = self.page.locator(target)
            answer.wait_for(state="visible")
            content.append(
                (question.inner_text().strip(), answer.inner_text().strip())
            )
        return content

    def get_video_source(self):
        iframe = self.page.locator("iframe[title='YouTube video player']")
        iframe.wait_for(state="visible")
        return iframe.get_attribute("src") or ""

    def play_video(self):
        iframe = self.page.locator("iframe[title='YouTube video player']")
        iframe.wait_for(state="visible")
        iframe.scroll_into_view_if_needed()

        frame = next(
            (
                candidate
                for candidate in self.page.frames
                if "youtube" in candidate.url.lower()
            ),
            None,
        )
        if frame is None:
            raise AssertionError("The YouTube player frame did not load.")

        video = frame.locator("video").first
        video.wait_for(state="attached", timeout=30000)
        initial_time = video.evaluate("element => element.currentTime")

        player_body = frame.locator("body")
        player_box = player_body.bounding_box()
        if not player_box:
            raise AssertionError("The YouTube player has no clickable area.")
        click_position = {
            "x": player_box["width"] / 2,
            "y": player_box["height"] / 2,
        }
        player_body.click(position=click_position, force=True)

        state = {}
        for attempt in range(60):
            state = video.evaluate(
                "element => ({"
                "paused: element.paused, "
                "current_time: element.currentTime, "
                "ready_state: element.readyState, "
                "error_code: element.error ? element.error.code : null"
                "})"
            )
            if not state["paused"] and state["current_time"] > initial_time:
                break
            if attempt and attempt % 10 == 0:
                player_body.click(position=click_position, force=True)
            self.page.wait_for_timeout(500)
        return state

    def open_quick_action(
        self,
        name,
        expected_path,
        expected_final_path=None,
        ready_locator=None,
    ):
        action = self.page.locator("a.btn-action", has_text=name)
        action.wait_for(state="visible")
        if action.inner_text().strip() != name:
            raise AssertionError(f"Quick Action {name!r} was not found.")

        href = action.get_attribute("href") or ""
        actual_path = urlparse(href).path
        if actual_path != expected_path:
            raise AssertionError(
                f"Quick Action {name!r} changed: expected {expected_path!r}, "
                f"found {actual_path!r}."
            )

        action.click()
        if expected_final_path:
            self.page.wait_for_url(f"**{expected_final_path}*")

        if ready_locator:
            for attempt in range(1, 4):
                try:
                    self.page.locator(ready_locator).first.wait_for(
                        state="visible", timeout=10000
                    )
                    break
                except PlaywrightTimeoutError:
                    if attempt == 3:
                        raise
                    self.page.reload(wait_until="domcontentloaded")
        return self

    def get_dealer_state_heading(self):
        for name in self.DEALER_STATE_HEADINGS:
            heading = self.page.get_by_role("heading", name=name, exact=True)
            if heading.is_visible():
                return heading.inner_text().strip()
        return None
