class FaqPage:
    def __init__(self, page):
        self.page = page

    def get_questions(self):
        questions = self.page.locator(
            "button[data-bs-toggle='collapse']:visible"
        )
        return [
            text.strip()
            for text in questions.all_inner_texts()
            if text.strip()
        ]

    def expand_first_question(self):
        question = self.page.locator(
            "button[data-bs-toggle='collapse']:visible"
        ).first
        question.wait_for(state="visible")
        question_text = question.inner_text().strip()
        target = question.get_attribute("data-bs-target")
        if not target:
            raise AssertionError("The first FAQ question has no answer target.")
        question.click()
        answer = self.page.locator(target)
        answer.wait_for(state="visible")
        return question_text, answer.inner_text().strip()

    def get_empty_question_form_validation_messages(self):
        form = self.page.get_by_role(
            "button", name="Send Question", exact=True
        ).locator("xpath=ancestor::form[1]")
        if form.evaluate("form => form.checkValidity()"):
            return {}

        required = form.locator("[required]")
        return {
            required.nth(index).get_attribute("name"): required.nth(
                index
            ).evaluate("field => field.validationMessage")
            for index in range(required.count())
        }
