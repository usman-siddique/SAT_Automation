from dataclasses import dataclass


@dataclass(frozen=True)
class NewCarVariant:
    """Selected New Car configuration carried through the purchase flow."""

    model: str
    variant: str
    color: str
    transmission: str
    drivetrain: str
    fuel: str
    seats: str
    car_price: str

    def features(self):
        return {
            "Color": self.color,
            "Transmission": self.transmission,
            "Drivetrain": self.drivetrain,
            "Fuel": self.fuel,
            "Seats": self.seats,
        }


@dataclass(frozen=True)
class NewCarPayPalPrices:
    """USD and converted JPY prices carried across the PayPal journey."""

    car_price_usd: str
    total_price_usd: str
    car_price_jpy: str
    total_price_jpy: str
