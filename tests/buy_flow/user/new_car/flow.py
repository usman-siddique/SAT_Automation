from config import (
    NEW_CAR_BANK_EXPECTED_VARIANT,
    NEW_CAR_BANK_MAKE,
    NEW_CAR_BANK_MODEL_SLUG,
    NEW_CAR_PAYGENT_EXPECTED_VARIANT,
    NEW_CAR_PAYGENT_MAKE,
    NEW_CAR_PAYGENT_MODEL_SLUG,
    NEW_CAR_PAYPAL_COUNTRY,
    NEW_CAR_PAYPAL_EXPECTED_VARIANT,
    NEW_CAR_PAYPAL_MAKE,
    NEW_CAR_PAYPAL_MODEL_SLUG,
    NEW_CAR_PAYPAL_PORT,
)
from pages.buy_flow.user.new_car.checkout_page import NewCarCheckoutPage
from pages.buy_flow.user.new_car.details_page import NewCarDetailsPage
from pages.buy_flow.user.new_car.home_page import NewCarHomePage
from pages.buy_flow.user.new_car.listing_page import NewCarListingPage
from pages.buy_flow.user.new_car.payment_page import NewCarPaymentPage


def open_new_car_payment(
    page,
    make: str,
    model_slug: str,
    expected_variant: dict,
    destination: tuple[str, str] | None = None,
):
    """Complete the User New Car journey through payment-page validation."""
    NewCarHomePage(page).open_from_header().show_cars()

    listing = NewCarListingPage(page)
    listing.select_make(make)
    listing.select_user_car(make, model_slug)

    details = NewCarDetailsPage(page)
    variant = details.verify_and_capture_variant(expected_variant)
    details.click_buy_now()

    checkout = NewCarCheckoutPage(page)
    if destination:
        checkout.select_destination(*destination)
    checkout_total = checkout.verify_variant_and_prices(variant)
    checkout.continue_to_payment()

    payment = NewCarPaymentPage(page)
    payment.verify_payment_summary(variant, checkout_total)
    if destination:
        payment.verify_payment_destination(*destination)
    return payment, variant, checkout_total


def open_new_car_paygent_payment(page):
    """Open the Nissan User New Car Paygent payment journey."""
    return open_new_car_payment(
        page,
        NEW_CAR_PAYGENT_MAKE,
        NEW_CAR_PAYGENT_MODEL_SLUG,
        NEW_CAR_PAYGENT_EXPECTED_VARIANT,
    )


def open_new_car_bank_payment(page):
    """Open the Honda User New Car Bank Transfer payment journey."""
    return open_new_car_payment(
        page,
        NEW_CAR_BANK_MAKE,
        NEW_CAR_BANK_MODEL_SLUG,
        NEW_CAR_BANK_EXPECTED_VARIANT,
    )


def open_new_car_paypal_payment(page):
    """Open the Toyota Aqua User New Car PayPal journey for UK/Bristol."""
    return open_new_car_payment(
        page,
        NEW_CAR_PAYPAL_MAKE,
        NEW_CAR_PAYPAL_MODEL_SLUG,
        NEW_CAR_PAYPAL_EXPECTED_VARIANT,
        destination=(NEW_CAR_PAYPAL_COUNTRY, NEW_CAR_PAYPAL_PORT),
    )
