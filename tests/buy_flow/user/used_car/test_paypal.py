import allure
import pytest

from config import (
    PAYPAL_SANDBOX_EMAIL,
    PAYPAL_SANDBOX_PASSWORD,
    USED_CAR_PAYPAL_COUNTRY,
    USED_CAR_PAYPAL_PORT,
    USED_CAR_PAYPAL_SHIPPING_TYPE,
    USED_CAR_PAYPAL_URL,
)
from pages.buy_flow.paypal_sandbox_page import PayPalSandboxPage
from pages.buy_flow.user.used_car.tracking_page import UsedCarTrackingPage
from tests.buy_flow.user.used_car.flow import open_used_car_paypal_payment


@pytest.mark.flaky(reruns=1, reruns_delay=2)
def test_used_car_order_with_paypal(require_state_changing_tests, page):
    if not PAYPAL_SANDBOX_EMAIL or not PAYPAL_SANDBOX_PASSWORD:
        raise RuntimeError(
            "PayPal sandbox credentials are missing from the private .env file."
        )

    print("\n" + "=" * 60)
    print("USER - USED CAR - PAYPAL ORDER FLOW")
    print("=" * 60)

    with allure.step(
        "Select available Suzuki and stabilize UK / Bristol RORO checkout"
    ):
        payment, snapshot = open_used_car_paypal_payment(
            page,
            USED_CAR_PAYPAL_URL,
            USED_CAR_PAYPAL_COUNTRY,
            USED_CAR_PAYPAL_PORT,
            USED_CAR_PAYPAL_SHIPPING_TYPE,
        )

    with allure.step(
        "Verify payment destination, shipping method, and USD breakdown"
    ):
        payment.verify_checkout_snapshot(snapshot)

    with allure.step("Select PayPal and verify real USD-to-JPY conversion"):
        prices = payment.select_paypal_and_capture_jpy(snapshot)

    with allure.step("Verify PayPal JPY total and approve sandbox payment"):
        payment.accept_terms()
        payment.submit_paypal()
        PayPalSandboxPage(page).login_and_approve(
            PAYPAL_SANDBOX_EMAIL,
            PAYPAL_SANDBOX_PASSWORD,
            prices.total_price_jpy,
            return_url_pattern="**/order-summary/**",
        )

    with allure.step("Verify SAT status, destination, and JPY price breakdown"):
        payment.verify_confirmation(snapshot, prices)

    with allure.step("Verify Track Your Order payment state and JPY total"):
        payment.open_tracking()
        UsedCarTrackingPage(page).verify_paypal_order(snapshot, prices)

    print(f"\nUsed Car PayPal order complete for {snapshot.stock_id.upper()}")
