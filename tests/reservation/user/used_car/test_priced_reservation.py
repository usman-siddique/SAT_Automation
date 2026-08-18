import allure

from config import USED_CAR_RESERVATION_URL
from pages.reservation.user.used_car.booking_page import BookingPage
from tests.reservation.user.used_car.flow import (
    open_priced_used_car_reservation,
)


@allure.title("User Used Car Reservation With Complete Price Breakdown")
def test_user_used_car_reservation_with_all_prices(
    require_state_changing_tests,
    page,
    tmp_path,
):
    with allure.step(
        "Find and submit an available Used Car reservation with numeric prices"
    ):
        reservation, snapshot = open_priced_used_car_reservation(
            page,
            USED_CAR_RESERVATION_URL,
        )

    with allure.step(
        "Verify Payment Pending confirmation, delivery, prices, and actions"
    ):
        reservation.verify_confirmation(snapshot)

    with allure.step("Download and verify the reservation invoice PDF"):
        reservation.download_and_verify_invoice(snapshot, tmp_path)

    with allure.step(
        "Open My Booking and verify the pending reservation and actions"
    ):
        reservation.open_view_reservation()
        BookingPage(page).verify_priced_reservation(snapshot)
