class FaqPage:
    SUBMISSION_PATH = "/faq-store"
    EXPECTED_CATEGORIES = (
        "Getting Started",
        "Choosing a Vehicle",
        "Pricing & Fees",
        "Buying & Auction",
        "Payment",
        "Inspection & Condition",
        "Shipping & Tracking",
        "Documentation",
        "Vehicle & Customs",
        "Cancellation & Refunds",
        "Dealers SAT & Loyalty",
        "Trust & Safety",
        "Glossary of Terms",
    )
    EXPECTED_QUESTION_COUNT = 103

    def __init__(self, page):
        self.page = page

    def get_faq_heading(self):
        heading = self.page.locator("h3.faq--title")
        heading.wait_for(state="visible")
        return heading.inner_text().strip()

    def get_search_placeholder(self):
        search = self.page.locator("#faq_search_input")
        search.wait_for(state="visible")
        return search.get_attribute("placeholder")

    def get_categories(self):
        return [
            text.strip()
            for text in self.page.locator("#faq-list li").all_inner_texts()
        ]

    def get_all_question_count(self):
        return self.page.locator(
            ".faqs--grid .tab-content "
            "button[data-bs-toggle='collapse']"
        ).count()

    def get_visible_questions(self):
        questions = self.page.locator(
            ".faqs--grid button[data-bs-toggle='collapse']:visible"
        )
        return [
            text.strip()
            for text in questions.all_inner_texts()
            if text.strip()
        ]

    def select_category(self, label):
        category = self.page.locator("#faq-list li", has_text=label)
        category.click()
        tab_id = category.get_attribute("data-tab")
        self.page.locator(f"#{tab_id}.active").wait_for(state="visible")
        return {
            "active": "active" in (category.get_attribute("class") or ""),
            "questions": self.get_visible_questions(),
        }

    def search(self, value):
        self.page.locator("#faq_search_input").fill(value)
        results = self.page.locator("#faq-search-results")
        no_results = self.page.locator("#faq-no-results")

        if value.strip():
            self.page.wait_for_function(
                """() =>
                    document.querySelector('#faq-search-results')
                        .classList.contains('active') ||
                    document.querySelector('#faq-no-results')
                        .classList.contains('active')"""
            )
        else:
            self.page.wait_for_function(
                """() =>
                    !document.querySelector('#faq-search-results')
                        .classList.contains('active') &&
                    !document.querySelector('#faq-no-results')
                        .classList.contains('active')"""
            )

        return {
            "questions": [
                text.strip()
                for text in results.locator(
                    "button[data-bs-toggle='collapse'] "
                    ".accord-btn-label"
                ).all_inner_texts()
                if text.strip()
            ]
            if results.is_visible()
            else [],
            "no_results": no_results.inner_text().strip()
            if no_results.is_visible()
            else "",
        }

    def expand_search_result(self, question_text):
        question = self.page.locator(
            "#faq-search-results button[data-bs-toggle='collapse']",
            has_text=question_text,
        )
        target = question.get_attribute("data-bs-target")
        if not target:
            raise AssertionError("The FAQ search result has no answer target.")
        question.click()
        answer = self.page.locator(target)
        answer.wait_for(state="visible")
        return answer.inner_text().strip()

    def get_question_form_details(self):
        form = self.page.locator("form[action$='/faq-store']")
        heading = self.page.get_by_role(
            "heading", name="Still Have Any Question?", exact=True
        )
        return {
            "heading": heading.inner_text().strip(),
            "question_required": form.locator(
                "textarea[name='question']"
            ).get_attribute("required")
            is not None,
            "name_required": form.locator(
                "input[name='name']"
            ).get_attribute("required")
            is not None,
            "email_required": form.locator(
                "input[name='email']"
            ).get_attribute("required")
            is not None,
            "email_type": form.locator(
                "input[name='email']"
            ).get_attribute("type"),
            "remember_visible": form.locator(
                "input[name='remember_details']"
            ).is_visible(),
            "submit_visible": form.get_by_role(
                "button", name="Send Question", exact=True
            ).is_visible(),
        }

    def get_question_form_validation(
        self,
        question,
        name,
        email,
        click_count=1,
    ):
        form = self.page.locator("form[action$='/faq-store']")
        submission_requests = []

        def record_submission(request):
            if (
                request.method == "POST"
                and self.SUBMISSION_PATH in request.url
            ):
                submission_requests.append(request)

        self.page.on("request", record_submission)
        try:
            form.locator("textarea[name='question']").fill(question)
            form.locator("input[name='name']").fill(name)
            form.locator("input[name='email']").fill(email)
            form.get_by_role(
                "button", name="Send Question", exact=True
            ).click(click_count=click_count)
            self.page.wait_for_timeout(200)

            field_states = {}
            for field_name in ("question", "name", "email"):
                field_states[field_name] = form.locator(
                    f"[name='{field_name}']"
                ).evaluate(
                    """field => ({
                        valid: field.validity.valid,
                        value_missing: field.validity.valueMissing,
                        type_mismatch: field.validity.typeMismatch,
                        message: field.validationMessage,
                    })"""
                )
            return {
                "fields": field_states,
                "post_count": len(submission_requests),
            }
        finally:
            self.page.remove_listener("request", record_submission)

    def check_remember_details(self):
        checkbox = self.page.locator(
            "form[action$='/faq-store'] input[name='remember_details']"
        )
        checkbox.check()
        return checkbox.is_checked()

    def submit_question(self, question, name, email):
        form = self.page.locator("form[action$='/faq-store']")
        form.locator("textarea[name='question']").fill(question)
        form.locator("input[name='name']").fill(name)
        form.locator("input[name='email']").fill(email)

        with self.page.expect_navigation(wait_until="commit") as navigation:
            with self.page.expect_response(
                lambda response: self.SUBMISSION_PATH in response.url
                and response.request.method == "POST"
            ) as response_info:
                form.get_by_role(
                    "button", name="Send Question", exact=True
                ).click()

        response = response_info.value
        navigation_response = navigation.value
        return {
            "status": response.status,
            "url": self.page.url,
            "navigation_status": navigation_response.status,
        }
