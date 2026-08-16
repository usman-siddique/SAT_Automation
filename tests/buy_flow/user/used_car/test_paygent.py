import allure
import pytest

from config import USED_CAR_PAYGENT_URL
from tests.buy_flow.user.used_car.flow import open_used_car_payment


@pytest.mark.flaky(reruns=1, reruns_delay=2)
def test_used_car_order_with_paygent(require_state_changing_tests, page):
    print("\n" + "=" * 60)
    print("USER - USED CAR - PAYGENT ORDER FLOW")
    print("=" * 60)

    with allure.step("Select an available Volkswagen and open Used Car checkout"):
        payment, stock_id = open_used_car_payment(page, USED_CAR_PAYGENT_URL)

    with allure.step("Select Paygent and capture the displayed total"):
        payment.select_credit_card()
        expected_total, total_requires_inquiry = (
            payment.get_selected_payment_total()
        )

    with allure.step("Enter card details and accept the purchase terms"):
        payment.fill_card_details("5555 5555 5555 4444", "12/34", "123")
        payment.accept_terms()

    with allure.step("Place the Paygent order and verify SAT confirmation"):
        payment.submit()
        payment.verify_order_confirmation(
            expected_total,
            total_requires_inquiry,
        )

    print(f"\nPaygent order placement complete for {stock_id.upper()}")
