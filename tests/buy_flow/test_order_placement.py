# tests/buy_flow/test_order_placement.py
import pytest
from pages.auth.login_page import LoginPage
from pages.buy_flow.used_cars_page import UsedCarsPage
from pages.buy_flow.car_details_page import CarDetailsPage
from pages.buy_flow.checkout_page import CheckoutPage
from pages.buy_flow.payment_page import PaymentPage

def test_complete_order_placement(require_state_changing_tests, page):
    print("\n" + "="*60)
    print("🚗 E2E ORDER PLACEMENT FLOW")
    print("="*60)

    # 1. Login (reuses existing session)
    login = LoginPage(page)
    login.login()

    # 2. Navigate to used cars and select a car with 'Inquire Now'
    used_cars = UsedCarsPage(page)
    used_cars.open(unreserved=True)
    used_cars.select_any_car_with_inquire_now()

    # 3. On car details page, click 'Buy Now'
    car_details = CarDetailsPage(page)
    car_details.click_buy_now()

    # 4. On checkout page, select services and continue
    checkout = CheckoutPage(page)
    checkout.select_services(["2", "3"])
    checkout.click_continue()

    # 5. On payment page, fill details, accept terms, submit, and verify confirmation
    payment = PaymentPage(page)
    payment.select_credit_card()
    payment.fill_card_details("5555 5555 5555 4444", "12/34", "123")
    payment.accept_terms()
    payment.submit()
    payment.verify_order_confirmation()

    print("\n✅ ORDER PLACEMENT COMPLETE")
