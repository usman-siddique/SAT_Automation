from pages.buy_flow.user.checkout_page import CheckoutPage
from pages.buy_flow.user.payment_page import PaymentPage
from pages.buy_flow.user.used_car.details_page import CarDetailsPage
from pages.buy_flow.user.used_car.inventory_page import UsedCarsPage
from pages.buy_flow.user.used_car.paypal_payment_page import (
    UsedCarPayPalPaymentPage,
)


def open_used_car_payment(page, inventory_url: str):
    """Complete the shared retail User Used Car journey up to payment."""
    used_cars = UsedCarsPage(page)
    used_cars.open(inventory_url)
    stock_id = used_cars.select_any_available_used_car()

    CarDetailsPage(page).click_buy_now()

    checkout = CheckoutPage(page)
    checkout.select_services(["2", "3"])
    checkout.click_continue()
    return PaymentPage(page), stock_id


def open_used_car_paypal_payment(
    page,
    inventory_url: str,
    country_name: str,
    port_name: str,
    shipping_type: str,
):
    """Open an available Used Car PayPal journey through stable checkout."""
    used_cars = UsedCarsPage(page)
    used_cars.open(inventory_url)
    stock_id = used_cars.select_any_available_used_car()

    CarDetailsPage(page).click_buy_now()

    checkout = CheckoutPage(page)
    snapshot = checkout.select_destination_and_shipping(
        stock_id,
        country_name,
        port_name,
        shipping_type,
    )
    checkout.click_continue()

    return UsedCarPayPalPaymentPage(page), snapshot
