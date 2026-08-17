import allure
import pytest

from config import USED_CAR_RESERVATION_URL
from pages.reservation.user.used_car.booking_page import BookingPage
from tests.reservation.user.used_car.flow import (
    open_priced_used_car_reservation,
)


@allure.title("User Used Car Reservation With Complete Price Breakdown")
@pytest.mark.flaky(reruns=1, reruns_delay=2)
def test_user_used_car_reservation_with_all_prices(
    require_state_changing_tests,
    page,
    tmp_path,
):
    with allure.step(
        "Select an available Used Car with automatic numeric reservation prices"
    ):
        reservation, snapshot = open_priced_used_car_reservation(
            page,
            USED_CAR_RESERVATION_URL,
        )

    with allure.step(
        "Verify destination, shipping, services, and prices on Submit Request"
    ):
        reservation.continue_to_review()
        reservation.verify_review(snapshot)

    with allure.step("Accept the reservation terms and submit the request"):
        reservation.submit_request()

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
