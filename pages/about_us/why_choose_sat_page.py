from urllib.parse import urlparse


class WhyChooseSatPage:
    PATH = "/why-choose-sat-japan"
    INTRO = (
        "At SAT Japan, we bring you a wide selection of premium used cars "
        "that combine quality, performance, and value. With global shipping "
        "and a strong commitment to quality and customer care, we ensure a "
        "smooth, secure, and satisfying experience at every step of the "
        "buying process"
    )
    SECTIONS = (
        (
            "Explore our Diverse Inventory",
            "Our extensive inventory displays an incredible collection of "
            "the finest Japanese used automobiles. From simple classics to "
            "the latest models, we have something in store for everyone. "
            "Use our Search Page to search for the car of you choice and get "
            "it shipped to your doorstep.",
            "diverse-inventory.webp",
        ),
        (
            "Shipping Automobiles Worldwide",
            "Get your hands on your favorite used Japanese car regardless of "
            "where you live. We offer export services globally, including "
            "continents such as Africa, South America, Asia, and Europe, so "
            "you can get your desired vehicle despite geographical limitations.",
            "shipping-automobile.webp",
        ),
        (
            "Commitment to Quality and Reliability",
            "Transform your driving experience with our reliable used "
            "Japanese vehicles. All our cars are carefully inspected to meet "
            "the highest standards of reliability. Our dedication to quality "
            "combined with cutting-edge Japanese engineering ensures that all "
            "our customers get superior driving experiences.",
            "satpro-paid-4.webp",
        ),
        (
            "Exceptional Customer Support",
            "Our team of professionals is devoted to providing personalized "
            "attention to each client and understanding their demands and "
            "preferences. We strive to satisfy your demands and ensure a "
            "smooth and hassle-free procurement journey. Feel free to ask us "
            "any question or send any inquiry at",
            "customer-support.webp",
        ),
    )

    def __init__(self, page):
        self.page = page

    def go_to_why_choose_sat(self):
        menu = self.page.locator("p.cnm-cls:has-text('About Us')").locator("..")
        menu.hover()
        link = menu.locator(".dropdown_content_header").get_by_role(
            "link", name="Why Choose SAT", exact=True
        )
        link.wait_for(state="visible")
        link.click()
        self.page.wait_for_url("**/why-choose-sat-japan", wait_until="domcontentloaded")
        self.page.locator("h1.why-title").wait_for(state="visible")
        assert urlparse(self.page.url).path.rstrip("/") == self.PATH

    def go_to_why_choose_sat_mobile(self):
        self.page.locator(
            "#menu_logo_mobile span[data-bs-target='#sidebarmobile']"
        ).click()
        self.page.locator("#sidebarmobile a.main-items-sidebar-content").filter(
            has_text="About Us"
        ).click()
        link = self.page.locator(
            "#offcanvascaroverview a[href$='/why-choose-sat-japan']"
        )
        link.wait_for(state="visible")
        link.click()
        self.page.wait_for_url("**/why-choose-sat-japan", wait_until="domcontentloaded")
        self.page.get_by_role(
            "heading", name="Why Choose SAT Japan?", exact=True
        ).wait_for(state="visible")
        assert urlparse(self.page.url).path.rstrip("/") == self.PATH

    def _section(self, title):
        return self.page.get_by_role(
            "heading", name=title, exact=True
        ).filter(visible=True).locator(
            "xpath=ancestor::div[contains(@class, 'row')][1]"
        )

    @staticmethod
    def _document_box(locator):
        return locator.evaluate(
            """element => {
                const box = element.getBoundingClientRect();
                return {
                    x: box.x + window.scrollX,
                    y: box.y + window.scrollY,
                    width: box.width,
                    height: box.height
                };
            }"""
        )

    def _verify_copy_and_images(self):
        hero = self.page.get_by_role(
            "heading", name="Why Choose SAT Japan?", exact=True
        ).filter(visible=True)
        assert hero.count() == 1, "Why Choose SAT hero heading is missing"
        intro = hero.locator("xpath=ancestor::div[contains(@class, 'row')][1]")
        assert self.INTRO in " ".join(intro.inner_text().split())

        sections = []
        for title, description, image_name in self.SECTIONS:
            section = self._section(title)
            assert section.count() == 1, f"Why Choose SAT section is missing: {title}"
            assert description in " ".join(section.inner_text().split()), (
                f"Why Choose SAT section copy is incomplete: {title}"
            )
            image = section.locator("img.satporpaid:visible")
            assert image.count() == 1, f"Why Choose SAT image is missing: {title}"
            assert image_name in (image.get_attribute("src") or ""), (
                f"Why Choose SAT section has the wrong image: {title}"
            )
            image.scroll_into_view_if_needed()
            image.evaluate(
                """element => new Promise((resolve, reject) => {
                    if (element.complete && element.naturalWidth > 0) {
                        resolve(true);
                        return;
                    }
                    const timeout = setTimeout(
                        () => reject(new Error('image load timeout')),
                        10000
                    );
                    element.addEventListener('load', () => {
                        clearTimeout(timeout);
                        resolve(true);
                    }, {once: true});
                    element.addEventListener('error', () => {
                        clearTimeout(timeout);
                        reject(new Error('image failed to load'));
                    }, {once: true});
                })"""
            )
            assert image.evaluate(
                "element => element.complete && element.naturalWidth > 0"
            ), f"Why Choose SAT image did not load: {title}"
            sections.append(section)
        return sections

    def verify_content_images_and_desktop_layout(self):
        sections = self._verify_copy_and_images()
        expected_image_on_right = (True, False, True, False)
        previous_bottom = 0

        for section, image_on_right in zip(sections, expected_image_on_right):
            heading = section.locator("h2.why-title:visible")
            image = section.locator("img.satporpaid:visible")
            section_box = self._document_box(section)
            heading_box = self._document_box(heading)
            image_box = self._document_box(image)
            assert section_box["y"] >= previous_bottom, (
                "Why Choose SAT desktop sections overlap"
            )
            previous_bottom = section_box["y"] + section_box["height"]
            if image_on_right:
                assert image_box["x"] > heading_box["x"], (
                    f"Desktop image should be on the right: {heading.inner_text()}"
                )
            else:
                assert image_box["x"] < heading_box["x"], (
                    f"Desktop image should be on the left: {heading.inner_text()}"
                )

    def verify_inquiry_link(self):
        link = self.page.locator("a[href$='/inquiry-form']:visible").filter(
            has_text="http://satjapan.com/inquiry-form"
        )
        assert link.count() == 1, "Why Choose SAT inquiry link is missing"
        href = link.get_attribute("href")
        assert urlparse(href).path == "/inquiry-form"
        response = self.page.request.get(
            href, fail_on_status_code=False, timeout=30000
        )
        assert response.status < 400, (
            f"Why Choose SAT inquiry link returned HTTP {response.status}"
        )
        assert urlparse(response.url).path.rstrip("/") == "/inquiry-form"
        link.click()
        self.page.wait_for_url("**/inquiry-form", wait_until="domcontentloaded")
        self.page.get_by_role(
            "heading", name="Inquiry Form:", exact=True
        ).wait_for(state="visible")

    def verify_mobile_content_and_layout(self):
        sections = self._verify_copy_and_images()
        layout = self.page.evaluate(
            """() => ({
                viewportWidth: visualViewport.width,
                documentWidth: document.documentElement.scrollWidth,
                bodyWidth: document.body.scrollWidth
            })"""
        )
        assert layout["viewportWidth"] > 0
        assert layout["documentWidth"] <= layout["viewportWidth"], (
            f"Why Choose SAT has horizontal mobile overflow: {layout}"
        )
        assert layout["bodyWidth"] <= layout["viewportWidth"], (
            f"Why Choose SAT body overflows on mobile: {layout}"
        )

        previous_bottom = 0
        for section in sections:
            section_box = self._document_box(section)
            image_box = self._document_box(section.locator("img.satporpaid:visible"))
            assert section_box["y"] >= previous_bottom, (
                "Why Choose SAT mobile sections overlap"
            )
            previous_bottom = section_box["y"] + section_box["height"]
            assert section_box["x"] >= 0
            assert (
                section_box["x"] + section_box["width"]
                <= layout["viewportWidth"]
            )
            assert image_box["x"] >= 0
            assert (
                image_box["x"] + image_box["width"]
                <= layout["viewportWidth"]
            )

        inquiry = self.page.locator("a[href$='/inquiry-form']:visible").filter(
            has_text="http://satjapan.com/inquiry-form"
        )
        assert inquiry.count() == 1
        inquiry_box = inquiry.bounding_box()
        assert inquiry_box["x"] >= 0
        assert (
            inquiry_box["x"] + inquiry_box["width"]
            <= layout["viewportWidth"]
        )
