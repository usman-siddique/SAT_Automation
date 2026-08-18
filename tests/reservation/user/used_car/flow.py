import allure
from allure_commons.types import AttachmentType

from pages.reservation.user.used_car.details_page import ReservationDetailsPage
from pages.reservation.user.used_car.reservation_page import (
    ReservationAlreadyExists,
    ReservationHasNoAskValue,
    ReservationPage,
    ReservationRequiresInquiry,
)


def _report_already_reserved(page, stock_id: str, error: Exception):
    with allure.step(
        "Skip already-reserved Used car "
        f"{stock_id.upper()} and try the next car"
    ):
        allure.attach(
            "\n".join(
                [
                    f"Stock ID: {stock_id.upper()}",
                    f"Site message: {error}",
                    "Action: skipped this car and returned to the "
                    "unreserved inventory.",
                    f"Review URL: {page.url}",
                ]
            ),
            name="Already-reserved car recovery",
            attachment_type=AttachmentType.TEXT,
        )
        try:
            screenshot = page.screenshot(full_page=True)
        except Exception as screenshot_error:
            allure.attach(
                str(screenshot_error),
                name="Already-reserved screenshot error",
                attachment_type=AttachmentType.TEXT,
            )
        else:
            allure.attach(
                screenshot,
                name=f"Already-reserved message - {stock_id.upper()}",
                attachment_type=AttachmentType.PNG,
            )
    print(
        "Skipping Used car because the site reports an existing "
        f"reservation: {stock_id.upper()} ({error})"
    )


def open_priced_used_car_reservation(page, inventory_url: str):
    """Submit the first available reservation with no Ask value."""
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
            reservation.continue_to_review()
            reservation.verify_review(snapshot)
            reservation.submit_request()
            return reservation, snapshot
        except ReservationAlreadyExists as error:
            excluded_stock_ids.add(candidate.stock_id.lower())
            _report_already_reserved(page, candidate.stock_id, error)
        except ReservationRequiresInquiry as error:
            excluded_stock_ids.add(candidate.stock_id.lower())
            print(
                "Skipping Used car because its reservation checkout requires "
                f"an inquiry: {candidate.stock_id.upper()} ({error})"
            )


def open_ask_used_car_reservation(page, inventory_url: str):
    """Submit the first candidate that produces ASK on reservation review."""
    excluded_stock_ids = set()
    details = ReservationDetailsPage(page)

    while True:
        stock_id = details.open_next_reservation_checkout(
            inventory_url,
            excluded_stock_ids,
        )
        reservation = ReservationPage(page)
        try:
            snapshot = reservation.capture_ask_checkout(stock_id)
            reservation.continue_to_review()
            snapshot = reservation.verify_ask_review(snapshot)
            reservation.submit_request()
            return reservation, snapshot
        except ReservationAlreadyExists as error:
            excluded_stock_ids.add(stock_id.lower())
            _report_already_reserved(page, stock_id, error)
        except ReservationHasNoAskValue as error:
            excluded_stock_ids.add(stock_id.lower())
            with allure.step(
                f"Skip {stock_id.upper()} because review has no ASK value"
            ):
                allure.attach(
                    str(error),
                    name="No ASK value found",
                    attachment_type=AttachmentType.TEXT,
                )
            print(
                "Skipping Used car because shipping and add-ons produced no "
                f"ASK value: {stock_id.upper()} ({error})"
            )
