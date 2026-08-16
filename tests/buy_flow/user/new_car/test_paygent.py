import allure
import pytest

from tests.buy_flow.user.new_car.flow import open_new_car_paygent_payment


@pytest.mark.flaky(reruns=1, reruns_delay=2)
def test_new_car_order_with_paygent(require_state_changing_tests, page):
    print("\n" + "=" * 60)
    print("USER - NEW CAR - PAYGENT ORDER FLOW")
    print("=" * 60)

    with allure.step("Select Nissan Dayz X and verify checkout/payment prices"):
        payment, variant, checkout_total = open_new_car_paygent_payment(page)

    with allure.step("Select Paygent and verify the displayed total"):
        payment.select_credit_card()
        payment.verify_selected_paygent_total(checkout_total)

    with allure.step("Enter card details and accept the purchase terms"):
        payment.fill_card_details("5555 5555 5555 4444", "12/34", "123")
        payment.accept_terms()

    with allure.step("Place the Paygent order and verify SAT confirmation"):
        payment.submit_new_car_paygent()
        payment.verify_new_car_confirmation(variant)

    print(f"\nNew Car Paygent order complete for {variant.model}")
