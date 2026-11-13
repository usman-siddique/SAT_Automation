"""Central test-card data used by payment automation.

These are public payment-provider test cards, not real card credentials. Change
``ACTIVE_TEST_CARD`` to exercise the other supported card without editing tests.
"""


TEST_PAYMENT_CARDS = {
    "mastercard": {
        "number": "5555 5555 5555 4444",
        "expiry": "12/34",
        "cvc": "123",
        "postal_code": "54000",
    },
    "visa": {
        "number": "4242 4242 4242 4242",
        "expiry": "12/34",
        "cvc": "123",
        "postal_code": "54000",
    },
}

ACTIVE_TEST_CARD = "mastercard"
