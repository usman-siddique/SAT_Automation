import allure
import pytest

from tests.buy_flow.user.new_car.flow import open_new_car_bank_payment


@pytest.mark.flaky(reruns=1, reruns_delay=2)
def test_new_car_order_with_bank_transfer(require_state_changing_tests, page):
    print("\n" + "=" * 60)
    print("USER - NEW CAR - BANK TRANSFER ORDER FLOW")
    print("=" * 60)

    with allure.step("Select Honda N-WGN G and verify checkout/payment prices"):
        payment, variant, checkout_total = open_new_car_bank_payment(page)

    with allure.step("Select Bank Transfer and verify the displayed total"):
        payment.select_bank_transfer()
        payment.verify_selected_bank_total(checkout_total)

    with allure.step("Accept the purchase terms and place the Bank order"):
        payment.accept_terms()
        payment.submit_new_car_bank_transfer()

    with allure.step("Verify Bank Transfer confirmation and payment details"):
        payment.verify_new_car_bank_confirmation(variant)

    print(f"\nNew Car Bank Transfer order complete for {variant.model}")
