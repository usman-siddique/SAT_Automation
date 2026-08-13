from config import (
    NEW_CAR_PAYGENT_EXPECTED_VARIANT,
    NEW_CAR_PAYGENT_MAKE,
    NEW_CAR_PAYGENT_MODEL_SLUG,
)
from pages.buy_flow.user.new_car.checkout_page import NewCarCheckoutPage
from pages.buy_flow.user.new_car.details_page import NewCarDetailsPage
from pages.buy_flow.user.new_car.home_page import NewCarHomePage
from pages.buy_flow.user.new_car.listing_page import NewCarListingPage
from pages.buy_flow.user.new_car.payment_page import NewCarPaymentPage


def open_new_car_paygent_payment(page):
    """Complete the User New Car journey through payment-page validation."""
    NewCarHomePage(page).open_from_header().show_cars()

    listing = NewCarListingPage(page)
    listing.select_make(NEW_CAR_PAYGENT_MAKE)
    listing.select_user_car(
        NEW_CAR_PAYGENT_MAKE,
        NEW_CAR_PAYGENT_MODEL_SLUG,
    )

    details = NewCarDetailsPage(page)
    variant = details.verify_and_capture_variant(
        NEW_CAR_PAYGENT_EXPECTED_VARIANT
    )
    details.click_buy_now()

    checkout = NewCarCheckoutPage(page)
    checkout_total = checkout.verify_variant_and_prices(variant)
    checkout.continue_to_payment()

    payment = NewCarPaymentPage(page)
    payment.verify_payment_summary(variant, checkout_total)
    return payment, variant, checkout_total
