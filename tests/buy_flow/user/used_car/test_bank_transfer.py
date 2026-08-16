import allure
import pytest

from config import USED_CAR_BANK_URL
from tests.buy_flow.user.used_car.flow import open_used_car_payment


@pytest.mark.flaky(reruns=1, reruns_delay=2)
def test_used_car_order_with_bank_transfer(require_state_changing_tests, page):
    print("\n" + "=" * 60)
    print("USER - USED CAR - BANK TRANSFER RESERVATION FLOW")
    print("=" * 60)

    with allure.step("Select an available Daihatsu and open Used Car checkout"):
        payment, stock_id = open_used_car_payment(page, USED_CAR_BANK_URL)

    with allure.step("Select Bank Transfer and capture the displayed total"):
        payment.select_bank_transfer()
        expected_total, total_requires_inquiry = (
            payment.get_selected_payment_total()
        )

    with allure.step("Accept the purchase terms and place the reservation"):
        payment.accept_terms()
        payment.submit_bank_transfer()

    with allure.step("Verify Bank Transfer status, invoice, and payment proof"):
        payment.verify_bank_reservation(
            expected_total,
            total_requires_inquiry,
        )

    print(f"\nBank Transfer reservation complete for {stock_id.upper()}")
