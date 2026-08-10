import pytest

from config import USED_CAR_BANK_URL
from tests.buy_flow.user.used_car.flow import open_used_car_payment


@pytest.mark.flaky(reruns=1, reruns_delay=2)
def test_used_car_order_with_bank_transfer(require_state_changing_tests, page):
    print("\n" + "=" * 60)
    print("USER - USED CAR - BANK TRANSFER RESERVATION FLOW")
    print("=" * 60)

    payment, stock_id = open_used_car_payment(page, USED_CAR_BANK_URL)
    payment.select_bank_transfer()
    expected_total, total_requires_inquiry = payment.get_selected_payment_total()
    payment.accept_terms()
    payment.submit_bank_transfer()
    payment.verify_bank_reservation(expected_total, total_requires_inquiry)

    print(f"\nBank Transfer reservation complete for {stock_id.upper()}")
