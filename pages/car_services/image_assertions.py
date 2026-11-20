"""Reliable image readiness checks for responsive and lazy-loaded media."""


def assert_image_loaded(image, description, timeout_ms=10000):
    image.scroll_into_view_if_needed()
    loaded = image.evaluate(
        """(element, timeout) => new Promise(resolve => {
            if (element.complete) {
                resolve(element.naturalWidth > 0);
                return;
            }
            const timer = setTimeout(() => resolve(false), timeout);
            element.addEventListener('load', () => {
                clearTimeout(timer);
                resolve(element.naturalWidth > 0);
            }, {once: true});
            element.addEventListener('error', () => {
                clearTimeout(timer);
                resolve(false);
            }, {once: true});
        })""",
        timeout_ms,
    )
    assert loaded, f"{description} failed to load."
