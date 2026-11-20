"""390 x 844 mobile-web coverage for priority Car Services flows."""

from decimal import Decimal

import allure

from config import (
    AUCTION_CALCULATOR_COUNTRY,
    AUCTION_CALCULATOR_PORT,
    AUCTION_CALCULATOR_STOCK_ID,
    NON_STOLEN_VEHICLE_DATA,
)
from pages.car_services.auction_service_page import AuctionServicePage
from pages.car_services.car_services_page import CarServicesPage
from pages.car_services.mobile_layout import MobileLayout
from pages.car_services.non_stolen_vehicle_page import NonStolenVehiclePage
from pages.car_services.pre_export_inspection_page import (
    PreExportInspectionPage,
)
from pages.car_services.shipping_schedule_page import ShippingSchedulePage
from pages.car_services.warranty_service_page import WarrantyServicePage


def test_car_services_mobile_menu_navigation(car_services_mobile_page):
    navigation = CarServicesPage(car_services_mobile_page)
    layout = MobileLayout(car_services_mobile_page)

    with allure.step("Verify every Car Services mobile-menu destination"):
        actual = navigation.get_mobile_menu_contract()
        expected = [
            {"name": name, "path": path}
            for name, path, _ in navigation.DESTINATIONS.values()
        ]
        assert len(actual) == len(expected)
        assert {item["path"]: item["name"] for item in actual} == {
            item["path"]: item["name"] for item in expected
        }
        submenu_links = car_services_mobile_page.locator(
            ".offcanvas:visible a:visible"
        )
        layout.assert_page("Car Services mobile menu", submenu_links)


def test_auction_calculator_mobile_layout_and_controls(
    car_services_mobile_page,
):
    navigation = CarServicesPage(car_services_mobile_page)
    navigation.go_to_auction_service_mobile()
    auction = AuctionServicePage(car_services_mobile_page)
    layout = MobileLayout(car_services_mobile_page)

    with allure.step("Verify Auction Service CTAs and responsive layout"):
        overview = auction.get_overview()
        assert overview["heading"] == "Auction Service Overview"
        layout.assert_page(
            "Auction Service",
            car_services_mobile_page.locator(
                ".auction-service-overview a:visible"
            ),
        )

    with allure.step("Verify the calculator and strict mobile cost controls"):
        auction.open_cost_calculator()
        data = auction.load_stock_data(
            AUCTION_CALCULATOR_STOCK_ID,
            AUCTION_CALCULATOR_COUNTRY,
            AUCTION_CALCULATOR_PORT,
        )
        assert data["bid_input"] > Decimal("0")
        assert data["country"] == AUCTION_CALCULATOR_COUNTRY
        assert data["port"] == AUCTION_CALCULATOR_PORT
        layout.assert_page(
            "Auction Cost Calculator",
            car_services_mobile_page.locator(
                "#stock_id:visible, #bidInput:visible, "
                "#destination_country_block button:visible, "
                "#destination_port_block button:visible, "
                "#downloadEstimate:visible"
            ),
        )


def test_shipping_schedule_mobile_filters_dates_and_tables(
    car_services_mobile_page,
):
    CarServicesPage(car_services_mobile_page).go_to_shipping_schedule_mobile()
    shipping = ShippingSchedulePage(car_services_mobile_page)
    layout = MobileLayout(car_services_mobile_page)

    with allure.step("Verify mobile schedule controls, cards, and tables"):
        contract = shipping.verify_mobile_page_contract()
        assert contract["path"] == "/shipping-schedule"
        schedules = shipping.verify_initial_schedule_data()
        assert shipping.expand_first_schedule() > 0
        layout.assert_page(
            "Shipping Schedule",
            car_services_mobile_page.locator(
                ".select2-selection:visible, input[class*='_date_']:visible, "
                ".btn-search-filter:visible, .btn-reset-filter:visible, "
                ".filter-data-card .expand:visible"
            ),
        )
        layout.assert_no_overlap(
            car_services_mobile_page.locator(".btn-search-filter:visible"),
            car_services_mobile_page.locator(".btn-reset-filter:visible"),
            "Shipping Search and Reset controls",
        )

    with allure.step("Verify all mobile date fields populate and reset"):
        for selector, day in (
            (".departure_date_from", 5),
            (".departure_date_to", 25),
            (".arrival_date_from", 5),
            (".arrival_date_to", 25),
        ):
            assert shipping.choose_date(selector, day)
        shipping.reset()

    with allure.step("Filter mobile schedules using live compatible data"):
        first = schedules[0]
        departure = first["fields"]["Departure Port"]
        ship = first["fields"]["Ship Name"]
        arrival = first["arrivals"][0]["port"]
        region = shipping.find_region_for_arrival(arrival)
        shipping.select_filters(departure, region, arrival, ship)
        shipping.search()
        assert shipping.verify_results_match(departure, arrival, ship) > 0


def test_non_stolen_vehicle_mobile_modal_and_validation(
    car_services_mobile_page,
):
    CarServicesPage(car_services_mobile_page).go_to_non_stolen_vehicle_mobile()
    non_stolen = NonStolenVehiclePage(car_services_mobile_page)
    layout = MobileLayout(car_services_mobile_page)

    with allure.step("Verify responsive content and Begin Verification CTA"):
        non_stolen.verify_overview_and_process()
        layout.assert_page(
            "Non-Stolen Vehicle",
            car_services_mobile_page.get_by_role(
                "button", name="Begin Verification", exact=True
            ),
        )

    with allure.step("Verify the mobile modal, form, and blocked invalid data"):
        non_stolen.open_modal()
        non_stolen.verify_form_contract()
        layout.assert_modal(non_stolen.modal, "Non-Stolen Vehicle modal")
        layout.assert_page(
            "Non-Stolen Vehicle modal",
            non_stolen.modal.locator(
                "#stock_id:visible, #email:visible, #call_phone:visible, "
                "#message:visible, #submitNonStolen:visible"
            ),
        )
        result = non_stolen.verify_negative_validation(
            NON_STOLEN_VEHICLE_DATA["valid_stock_id"],
            NON_STOLEN_VEHICLE_DATA["invalid_stock_id"],
        )
        assert result["payment_requests"] == []


def test_warranty_mobile_faqs_and_responsive_table(
    car_services_mobile_page,
):
    CarServicesPage(car_services_mobile_page).go_to_warranty_service_mobile()
    warranty = WarrantyServicePage(car_services_mobile_page)
    layout = MobileLayout(car_services_mobile_page)

    with allure.step("Verify Warranty mobile content and coverage table"):
        contract = warranty.verify_page_contract()
        assert contract["path"] == "/sat-warranty"
        assert len(warranty.verify_coverage_limits()) == 4
        layout.assert_page(
            "SAT Japan Warranty",
            car_services_mobile_page.locator(
                "table:visible, button.accordion-button:visible"
            ),
        )

    with allure.step("Open and verify every mobile Warranty FAQ"):
        faqs = warranty.open_visible_faqs()
        assert faqs["questions"] == warranty.FAQ_QUESTIONS
        assert all(faqs["answers"])


def test_pre_export_mobile_content_and_pdf_action(
    car_services_mobile_page,
    tmp_path,
):
    CarServicesPage(
        car_services_mobile_page
    ).go_to_pre_export_inspection_mobile()
    pre_export = PreExportInspectionPage(car_services_mobile_page, tmp_path)
    layout = MobileLayout(car_services_mobile_page)

    with allure.step("Verify Pre-Export mobile content and report CTA"):
        overview = pre_export.verify_overview_and_refund_policy()
        assert overview["path"] == "/pre-export-inspection"
        layout.assert_page(
            "Pre-Export Inspection",
            car_services_mobile_page.locator(
                "a[download][href$='.pdf']:visible"
            ),
        )

    with allure.step("Download and validate the mobile sample PDF action"):
        report = pre_export.download_sample_report()
        assert report["filename"].lower().endswith(".pdf")
        assert report["size"] > 1000
