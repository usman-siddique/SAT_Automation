import re


class BankInformationPage:
    CURRENCY_SECTIONS = (
        "USD",
        "EUR",
        "JPY",
        "AUD",
        "GBP",
        "NZD",
        "CAD",
        "CNY",
    )

    def __init__(self, page):
        self.page = page

    @staticmethod
    def _clean(text):
        return " ".join(text.split()).strip()

    def get_bank_sections(self):
        sections = self.page.locator(
            "#v-pills-Bank-Information > section"
        )
        result = {}

        for section_index in range(sections.count()):
            section = sections.nth(section_index)
            heading = self._clean(
                section.locator(".bank-info-top-hdr").inner_text()
            )
            currency_match = re.fullmatch(
                r"Bank Information \(([A-Z]{3})\)", heading
            )
            if not currency_match:
                raise AssertionError(
                    f"Unexpected bank-information heading: {heading!r}"
                )

            banks = []
            rows = section.locator(":scope > .row.mt-4.mb-4")
            for row_index in range(rows.count()):
                row = rows.nth(row_index)
                labels = row.locator(".bank-name-label")
                values = row.locator(".bank-name-label-spn")
                if labels.count() != values.count():
                    raise AssertionError(
                        f"Mismatched bank labels and values in {heading}."
                    )

                details = {}
                for detail_index in range(labels.count()):
                    label = self._clean(
                        labels.nth(detail_index).inner_text()
                    ).rstrip(":")
                    value = self._clean(
                        values.nth(detail_index).inner_text()
                    )
                    details[label] = value
                banks.append(details)

            result[currency_match.group(1)] = banks

        return result

    def get_currency_icon_states(self):
        sections = self.page.locator(
            "#v-pills-Bank-Information > section"
        )
        return [
            sections.nth(index)
            .locator("img.bank-info-top-img")
            .evaluate("image => image.complete && image.naturalWidth > 0")
            for index in range(sections.count())
        ]
