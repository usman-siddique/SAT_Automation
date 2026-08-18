import allure

from config import USED_CAR_RESERVATION_URL
from pages.reservation.user.used_car.booking_page import BookingPage
from tests.reservation.user.used_car.flow import open_ask_used_car_reservation


@allure.title("User Used Car Reservation With ASK Price Breakdown")
def test_user_used_car_reservation_with_ask_prices(
    require_state_changing_tests,
    page,
):
    with allure.step(
        "Find and submit a Used Car reservation with an ASK price"
    ):
        reservation, snapshot = open_ask_used_car_reservation(
            page,
            USED_CAR_RESERVATION_URL,
        )

    with allure.step(
        "Verify Payment Pending, ASK breakdown, and pending invoice guidance"
    ):
        reservation.verify_ask_confirmation(snapshot)

    with allure.step(
        "Open My Booking and verify the ASK reservation is Invoice Pending"
    ):
        reservation.open_view_reservation()
        BookingPage(page).verify_ask_reservation(snapshot)
