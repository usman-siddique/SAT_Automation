import re
from dataclasses import dataclass


def normalize_price(value: str):
    """Return comparable numeric price text without currency formatting."""
    normalized = re.sub(r"[^0-9.]", "", value)
    if not normalized:
        raise AssertionError(f"Numeric price was not found in {value!r}.")
    return normalized


def normalize_text(value: str):
    """Return case-insensitive alphanumeric text for UI comparisons."""
    return re.sub(r"[^a-z0-9]", "", value.lower())


@dataclass(frozen=True)
class ReservationCandidate:
    """Reservation values retained from a valid Used Car detail page."""

    stock_id: str
    country: str
    port: str
    shipping_method: str
    selected_services: tuple[str, ...]
    car_price_usd: str
    shipping_cost_usd: str
    total_price_usd: str


@dataclass(frozen=True)
class ReservationSnapshot:
    """Priced reservation values retained across all remaining pages."""

    stock_id: str
    country: str
    port: str
    shipping_method: str
    selected_services: tuple[str, ...]
    price_breakdown: tuple[tuple[str, str], ...]

    def price(self, label: str):
        expected_label = normalize_text(label)
        for actual_label, value in self.price_breakdown:
            if normalize_text(actual_label) == expected_label:
                return value
        raise AssertionError(
            f"Reservation price {label!r} was not captured: "
            f"{self.price_breakdown}."
        )


@dataclass(frozen=True)
class AskReservationSnapshot:
    """ASK reservation values retained from checkout through My Booking."""

    stock_id: str
    country: str
    port: str
    shipping_method: str
    selected_services: tuple[str, ...]
    unavailable_services: tuple[str, ...]
    selected_add_ons: tuple[str, ...]
    checkout_breakdown: tuple[tuple[str, str], ...]
    review_breakdown: tuple[tuple[str, str], ...] = ()

    @staticmethod
    def _value(
        breakdown: tuple[tuple[str, str], ...],
        label: str,
    ):
        expected_label = normalize_text(label)
        for actual_label, value in breakdown:
            if normalize_text(actual_label) == expected_label:
                return value
        raise AssertionError(
            f"ASK reservation value {label!r} was not captured: "
            f"{breakdown}."
        )

    def checkout_price(self, label: str):
        return self._value(self.checkout_breakdown, label)

    def review_price(self, label: str):
        return self._value(self.review_breakdown, label)
