"""Strict responsive-layout assertions for Car Services mobile tests."""


class MobileLayout:
    WIDTH = 390
    HEIGHT = 844
    TOLERANCE = 1

    def __init__(self, page):
        self.page = page

    def assert_page(self, page_name, controls=None):
        metrics = self.page.evaluate(
            """() => ({
                innerWidth,
                innerHeight,
                documentWidth: document.documentElement.scrollWidth,
                bodyWidth: document.body.scrollWidth
            })"""
        )
        assert metrics["innerWidth"] == self.WIDTH, metrics
        assert metrics["innerHeight"] == self.HEIGHT, metrics
        assert metrics["documentWidth"] <= (
            metrics["innerWidth"] + self.TOLERANCE
        ), f"{page_name} has horizontal document overflow: {metrics}"
        assert metrics["bodyWidth"] <= (
            metrics["innerWidth"] + self.TOLERANCE
        ), f"{page_name} has horizontal body overflow: {metrics}"
        assert self.page.locator("#navbar_mobile_header").is_visible(), (
            f"{page_name} is missing the mobile header."
        )

        if controls is not None:
            assert controls.count() > 0, f"{page_name} has no usable controls."
            for index in range(controls.count()):
                control = controls.nth(index)
                if not control.is_visible():
                    continue
                control.scroll_into_view_if_needed()
                box = control.bounding_box()
                assert box and box["width"] > 0 and box["height"] > 0, (
                    f"{page_name} control {index + 1} has no usable size."
                )
                assert box["x"] >= -self.TOLERANCE, (
                    f"{page_name} control {index + 1} is clipped left: {box}"
                )
                assert box["x"] + box["width"] <= (
                    metrics["innerWidth"] + self.TOLERANCE
                ), (
                    f"{page_name} control {index + 1} is clipped right: {box}"
                )
        return metrics

    def assert_modal(self, modal, modal_name):
        modal.wait_for(state="visible")
        box = modal.bounding_box()
        assert box and box["width"] > 0 and box["height"] > 0
        assert box["x"] >= -self.TOLERANCE, (
            f"{modal_name} is clipped on the left: {box}"
        )
        assert box["x"] + box["width"] <= self.WIDTH + self.TOLERANCE, (
            f"{modal_name} is clipped on the right: {box}"
        )
        assert modal.evaluate(
            "element => element.scrollHeight <= element.clientHeight || "
            "['auto', 'scroll'].includes(getComputedStyle(element).overflowY)"
        ), f"{modal_name} content is clipped without vertical scrolling."

    def assert_internal_horizontal_scroll(self, container, content, name):
        container.scroll_into_view_if_needed()
        state = container.evaluate(
            """(element, content) => ({
                clientWidth: element.clientWidth,
                scrollWidth: element.scrollWidth,
                overflowX: getComputedStyle(element).overflowX,
                contentWidth: content.scrollWidth
            })""",
            content.element_handle(),
        )
        assert state["contentWidth"] > 0, f"{name} has no rendered content."
        if state["contentWidth"] > state["clientWidth"]:
            assert state["overflowX"] in ("auto", "scroll"), (
                f"{name} is clipped without horizontal scrolling: {state}"
            )
        return state

    def assert_no_overlap(self, first, second, description):
        first.scroll_into_view_if_needed()
        first_box = first.bounding_box()
        second_box = second.bounding_box()
        assert first_box and second_box
        horizontal = max(
            0,
            min(
                first_box["x"] + first_box["width"],
                second_box["x"] + second_box["width"],
            ) - max(first_box["x"], second_box["x"]),
        )
        vertical = max(
            0,
            min(
                first_box["y"] + first_box["height"],
                second_box["y"] + second_box["height"],
            ) - max(first_box["y"], second_box["y"]),
        )
        assert horizontal * vertical <= self.TOLERANCE, (
            f"{description} overlap: {first_box} vs {second_box}"
        )
