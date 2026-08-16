from dataclasses import dataclass


@dataclass(frozen=True)
class UsedCarCheckoutSnapshot:
    """Used Car shipping and USD prices captured before payment selection."""

    stock_id: str
    country: str
    port: str
    shipping_method: str
    car_price_usd: str
    shipping_cost_usd: str
    insurance_usd: str
    warranty_usd: str
    total_price_usd: str

    @property
    def shipping_requires_inquiry(self):
        return self.shipping_cost_usd.strip().lower() == "ask"


@dataclass(frozen=True)
class UsedCarPayPalPrices:
    """Used Car JPY breakdown captured after PayPal selection."""

    car_price_jpy: str
    shipping_cost_jpy: str
    insurance_jpy: str
    warranty_jpy: str
    total_price_jpy: str
