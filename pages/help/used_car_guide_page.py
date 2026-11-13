class UsedCarGuidePage:
    MAIN_HEADINGS = (
        "Overview",
        "Choose a Used Car by Category",
        "Determine the Purpose of Purchase",
        "Make the Purchase Process Convenient with SAT",
    )
    CATEGORY_HEADINGS = (
        "1. Used Sedan",
        "Why Choose a Sedan?",
        "2. Used SUV",
        "Why Choose an SUV?",
        "3. Used Hatchback",
        "Why Choose a Hatchback?",
        "4. Used Minivans",
        "Why Choose a Minivan?",
        "5. Used Off-Road Cars",
        "Why Choose an Off-Road Car?",
        "6. Used Trucks",
        "Why Choose a Truck?",
    )
    PURCHASE_QUESTIONS = (
        "Where will the car be used mostly?",
        "Does the vehicle cost fit in my budget?",
        "Will the vehicle usually travel long distances?",
        "Does the vehicle have specific features?",
    )

    def __init__(self, page):
        self.page = page

    def get_banner_content(self):
        banner = self.page.locator(".hcb")
        return {
            "title": banner.locator(".hcb__title").inner_text().strip(),
            "description": banner.locator(".hcb__para").inner_text().strip(),
        }

    def get_guide_headings(self):
        headings = []
        for name in self.MAIN_HEADINGS:
            heading = self.page.get_by_role("heading", name=name, exact=True)
            heading.wait_for(state="visible")
            headings.append(heading.inner_text().strip())
        return headings

    def get_overview_content(self):
        overview = self.page.locator(".how-to-choose-main")
        return {
            "overview": overview.locator(
                ".how-to-chose-comman-para"
            ).inner_text().strip(),
            "buyer_guide_heading": overview.locator(
                ".how-to-chose-detail-hdr"
            ).inner_text().strip(),
            "buyer_guide": overview.locator(
                ".how-to-chose-detail-para"
            ).inner_text().strip(),
        }

    def get_category_content(self):
        section = self.page.locator(".used-car-category")
        return {
            "headings": [
                text.strip()
                for text in section.locator(
                    ".choose-used-car-category-hdr"
                ).all_inner_texts()
            ],
            "descriptions": [
                text.strip()
                for text in section.locator(
                    ".choose-used-car-category-para"
                ).all_inner_texts()
            ],
        }

    def get_purchase_questions(self):
        return [
            text.strip()
            for text in self.page.locator(
                ".determine-purpose-purchase .purchase-purpose-para"
            ).all_inner_texts()
        ]

    def get_closing_content(self):
        section = self.page.locator(".purchase-min-div")
        return {
            "heading": section.locator(
                ".how-to-chose-comman-hdr"
            ).inner_text().strip(),
            "description": section.locator(
                ".how-to-chose-comman-para"
            ).inner_text().strip(),
        }

    def get_main_image_status(self):
        images = self.page.locator(
            ".hcb img:visible, "
            ".how-to-choose-main img:visible, "
            ".used-car-category img:visible"
        )
        return [
            images.nth(index).evaluate(
                """image => ({
                    loaded: image.complete && image.naturalWidth > 0,
                    src: image.currentSrc || image.src,
                })"""
            )
            for index in range(images.count())
        ]

    def scroll_to_page_end(self):
        position = self.page.evaluate(
            """async () => {
                const pause = (ms) => new Promise(resolve =>
                    setTimeout(resolve, ms));

                for (let pass = 0; pass < 3; pass += 1) {
                    const step = Math.max(window.innerHeight * 0.8, 500);
                    while (
                        window.scrollY + window.innerHeight <
                        document.documentElement.scrollHeight - 5
                    ) {
                        window.scrollBy(0, step);
                        await pause(40);
                    }
                    window.scrollTo(0, document.documentElement.scrollHeight);
                    await pause(250);
                }

                return {
                    scroll_y: window.scrollY,
                    viewport_height: window.innerHeight,
                    page_height: document.documentElement.scrollHeight,
                };
            }"""
        )
        footer = self.page.locator("#main_footer")
        return {
            **position,
            "footer_visible": footer.is_visible(),
            "contact_heading_visible": footer.get_by_role(
                "heading", name="Contact Us", exact=True
            ).is_visible(),
        }
