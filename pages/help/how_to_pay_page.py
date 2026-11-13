from urllib.parse import urlparse


class HowToPayPage:
    def __init__(self, page):
        self.page = page

    def get_main_heading(self):
        heading = self.page.get_by_role("heading", name="How to Pay", exact=True)
        heading.wait_for(state="visible")
        return heading.inner_text().strip()

    def get_intro_text(self):
        intro = self.page.locator(".how-py-top-paragraph")
        intro.wait_for(state="visible")
        return intro.inner_text().strip()

    def get_payment_methods(self):
        cards = self.page.locator(
            "#v-pills-How-to-Pay .aution-ser-col-min"
        )
        methods = []
        for index in range(cards.count()):
            card = cards.nth(index)
            image = card.locator("img.how-to-py-icons")
            methods.append(
                {
                    "heading": card.locator(
                        ".how-pay-crd-hdr"
                    ).inner_text().strip(),
                    "description": card.locator(
                        ".how-to-py-paragrp"
                    ).inner_text().strip(),
                    "icon_loaded": image.evaluate(
                        "image => image.complete && image.naturalWidth > 0"
                    ),
                }
            )
        return methods

    def get_sidebar_links(self):
        items = self.page.locator(
            "#dashboard_selection .dash-item-1 "
            ".sticy-items-dashboard li"
        )
        return [
            {
                "label": items.nth(index).inner_text().strip(),
                "path": urlparse(
                    items.nth(index).locator("a").get_attribute("href")
                ).path,
                "active": "selected-option"
                in (items.nth(index).get_attribute("class") or ""),
            }
            for index in range(items.count())
        ]
