import allure
import pytest

from config import (
    NEW_CAR_PAYPAL_COUNTRY,
    NEW_CAR_PAYPAL_PORT,
    PAYPAL_SANDBOX_EMAIL,
    PAYPAL_SANDBOX_PASSWORD,
)
from pages.buy_flow.paypal_sandbox_page import PayPalSandboxPage
from pages.buy_flow.user.new_car.tracking_page import NewCarTrackingPage
from tests.buy_flow.user.new_car.flow import open_new_car_paypal_payment


@pytest.mark.flaky(reruns=1, reruns_delay=2)
def test_new_car_order_with_paypal(require_state_changing_tests, page):
    if not PAYPAL_SANDBOX_EMAIL or not PAYPAL_SANDBOX_PASSWORD:
        raise RuntimeError(
            "PayPal sandbox credentials are missing from the private .env file."
        )

    print("\n" + "=" * 60)
    print("USER - NEW CAR - PAYPAL ORDER FLOW")
    print("=" * 60)

    with allure.step(
        "Select Nissan Roox S and manually set United Kingdom / Bristol"
    ):
        payment, variant, checkout_total_usd = open_new_car_paypal_payment(page)

    with allure.step("Select PayPal and capture the converted JPY prices"):
        prices = payment.select_paypal_and_capture_jpy_prices(
            variant,
            checkout_total_usd,
        )

    with allure.step("Verify PayPal JPY total and approve sandbox payment"):
        payment.accept_terms()
        payment.submit_new_car_paypal()
        PayPalSandboxPage(page).login_and_approve(
            PAYPAL_SANDBOX_EMAIL,
            PAYPAL_SANDBOX_PASSWORD,
            prices.total_price_jpy,
        )

    with allure.step("Verify SAT PayPal order confirmation"):
        payment.verify_new_car_paypal_confirmation(
            variant,
            prices,
            NEW_CAR_PAYPAL_COUNTRY,
            NEW_CAR_PAYPAL_PORT,
        )

    with allure.step("Verify Track Your Order amount, destination, and variant"):
        payment.open_tracking()
        NewCarTrackingPage(page).verify_paypal_order(
            variant,
            prices,
            NEW_CAR_PAYPAL_COUNTRY,
            NEW_CAR_PAYPAL_PORT,
        )

    print(f"\nNew Car PayPal order complete for {variant.model}")
