import re

from playwright.sync_api import Page

from pages.buy_flow.user.new_car.variant import NewCarVariant


class NewCarDetailsPage:
    def __init__(self, page: Page):
        self.page = page

    def _selected_value(self, label: str):
        control = self.page.locator("button.satSelectBtn").filter(
            has=self.page.locator(
                "span.type",
                has_text=re.compile(rf"^{re.escape(label)}$", re.IGNORECASE),
            )
        ).first
        control.wait_for(state="visible")
        value = control.locator("span.button-text").inner_text().strip()
        assert value and value.lower() != "select", (
            f"New Car {label} does not have a selected value."
        )
        return value

    def verify_and_capture_variant(self, expected: dict):
        """Assert the configured admin variant and capture its current price."""
        expected_model = expected["model"]
        self.page.get_by_text(expected_model, exact=True).first.wait_for(
            state="visible"
        )

        selected = {
            "variant": self._selected_value("Nissan DAYZ Variants"),
            "color": self._selected_value("Color"),
            "transmission": self._selected_value("Transmission"),
            "drivetrain": self._selected_value("Drivetrain"),
            "fuel": self._selected_value("Fuel"),
            "seats": self._selected_value("Seats"),
        }
        for field, actual in selected.items():
            assert actual == expected[field], (
                f"New Car {field} does not match the expected admin data: "
                f"expected {expected[field]!r}, found {actual!r}."
            )

        price = self.page.locator("#carPrice")
        price.wait_for(state="visible")
        car_price = price.inner_text().strip()
        assert re.sub(r"[^0-9.]", "", car_price), (
            f"New Car price is invalid: {car_price!r}"
        )

        buy_now = self.page.locator("button.detail-btn.buy--now").first
        inquire = self.page.locator("button.detail-btn.inquire--now").first
        buy_now.wait_for(state="visible")
        inquire.wait_for(state="visible")
        assert buy_now.is_enabled(), "New Car Buy Now button is disabled"
        assert inquire.is_enabled(), "New Car Inquire button is disabled"

        snapshot = NewCarVariant(
            model=expected_model,
            variant=selected["variant"],
            color=selected["color"],
            transmission=selected["transmission"],
            drivetrain=selected["drivetrain"],
            fuel=selected["fuel"],
            seats=selected["seats"],
            car_price=car_price,
        )
        print(
            "Verified New Car variant: "
            f"{snapshot.variant}, {snapshot.color}, {snapshot.transmission}, "
            f"{snapshot.drivetrain}, {snapshot.fuel}, {snapshot.seats} seats, "
            f"price {snapshot.car_price}"
        )
        return snapshot

    def click_buy_now(self):
        buy_now = self.page.locator("button.detail-btn.buy--now").first
        buy_now.wait_for(state="visible")
        buy_now.click()
        self.page.wait_for_url("**/new-car-checkout/**")
        print("Opened New Car checkout")
        return self
