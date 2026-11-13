"""Business coverage for the Shipping Schedule page."""

import allure

from pages.car_services.car_services_page import CarServicesPage
from pages.car_services.shipping_schedule_page import ShippingSchedulePage


def open_shipping_schedule(page):
    CarServicesPage(page).go_to_shipping_schedule()
    return ShippingSchedulePage(page)


def get_live_filter_data(shipping):
    schedules = shipping.verify_initial_schedule_data()
    first = schedules[0]
    departure = first["fields"]["Departure Port"]
    ship = first["fields"]["Ship Name"]
    arrival = first["arrivals"][0]["port"]
    region = shipping.find_region_for_arrival(arrival)
    return schedules, departure, region, arrival, ship


def test_shipping_schedule_page_and_schedule_details(page_no_login):
    shipping = open_shipping_schedule(page_no_login)

    with allure.step("Verify page content and all schedule controls"):
        assert shipping.verify_page_contract() == {
            "path": "/shipping-schedule",
            "heading": "Shipping Schedule",
            "intro_present": True,
            "controls_visible": True,
        }

    with allure.step("Verify live schedule fields and expandable arrival data"):
        shipping.verify_initial_schedule_data()
        assert shipping.expand_first_schedule() > 0

    with allure.step("Verify the Shipping Notes link and all six notices"):
        assert shipping.verify_shipping_notes() == 6


def test_shipping_schedule_positive_filters_and_dates(page_no_login):
    shipping = open_shipping_schedule(page_no_login)
    (
        _,
        departure,
        region,
        arrival,
        ship,
    ) = get_live_filter_data(shipping)

    with allure.step("Filter using a live schedule and verify every result"):
        shipping.select_filters(departure, region, arrival, ship)
        query = shipping.search()
        assert set(
            ("departure_port", "region", "arrival_port", "ship_name")
        ).issubset(query)
        assert shipping.verify_results_match(
            departure, arrival, ship
        ) > 0

    with allure.step("Reset filters and restore the complete schedule"):
        shipping.reset()

    with allure.step("Verify all four date pickers populate and reset"):
        selected_dates = {
            shipping.choose_date(".departure_date_from", 5),
            shipping.choose_date(".departure_date_to", 25),
            shipping.choose_date(".arrival_date_from", 5),
            shipping.choose_date(".arrival_date_to", 25),
        }
        assert len(selected_dates) >= 2
        shipping.reset()


def test_shipping_schedule_incompatible_filters_show_no_results(
    page_no_login,
):
    shipping = open_shipping_schedule(page_no_login)
    (
        schedules,
        _,
        region,
        arrival,
        ship,
    ) = get_live_filter_data(shipping)

    with allure.step("Build an incompatible combination from live data"):
        used_departures = {
            schedule["fields"]["Departure Port"]
            for schedule in schedules
            if schedule["fields"]["Ship Name"] == ship
            and any(
                item["port"] == arrival
                for item in schedule["arrivals"]
            )
        }
        invalid_departure = next(
            departure
            for departure in shipping.get_filter_options("departure_port")
            if departure not in used_departures
        )

    with allure.step("Verify incompatible filters return no schedules"):
        shipping.select_filters(
            invalid_departure,
            region,
            arrival,
            ship,
        )
        shipping.search()
        assert shipping.verify_no_results()
