from pages.reservation.user.used_car.details_page import ReservationDetailsPage
from pages.reservation.user.used_car.reservation_page import (
    ReservationPage,
    ReservationRequiresInquiry,
)


def open_priced_used_car_reservation(page, inventory_url: str):
    """Open the first reservation whose selected breakdown has no Ask value."""
    excluded_stock_ids = set()
    details = ReservationDetailsPage(page)

    while True:
        candidate = details.open_next_priced_reservation(
            inventory_url,
            excluded_stock_ids,
        )
        reservation = ReservationPage(page)
        try:
            snapshot = reservation.capture_priced_checkout(candidate)
            return reservation, snapshot
        except ReservationRequiresInquiry as error:
            excluded_stock_ids.add(candidate.stock_id.lower())
            print(
                "Skipping Used car because its reservation checkout requires "
                f"an inquiry: {candidate.stock_id.upper()} ({error})"
            )
