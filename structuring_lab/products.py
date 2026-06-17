from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ProductResult:
    terminal_price: float
    settlement_value_quote: float
    benchmark_value_quote: float
    converted: bool

    @property
    def benchmark_gap(self) -> float:
        return self.settlement_value_quote - self.benchmark_value_quote


@dataclass(frozen=True)
class DualCurrencyInvestment:
    """Dual Currency Investment approximation in quote-value terms.

    side="put":
        Client deposits stablecoin. If terminal price is below strike, principal
        plus coupon is converted into BTC at strike.

    side="call":
        Client deposits BTC. If terminal price is above strike, BTC plus coupon
        is converted into stablecoin at strike.
    """

    spot: float
    strike: float
    notional_quote: float
    apr: float
    tenor_days: int
    side: str = "put"

    def __post_init__(self) -> None:
        if self.spot <= 0 or self.strike <= 0 or self.notional_quote <= 0:
            raise ValueError("spot, strike, and notional_quote must be positive")
        if self.tenor_days <= 0:
            raise ValueError("tenor_days must be positive")
        if self.side not in {"put", "call"}:
            raise ValueError("side must be put or call")

    @property
    def tenor_years(self) -> float:
        return self.tenor_days / 365.0

    @property
    def coupon_quote(self) -> float:
        return self.notional_quote * self.apr * self.tenor_years

    @property
    def base_quantity(self) -> float:
        return self.notional_quote / self.spot

    def evaluate(self, terminal_price: float) -> ProductResult:
        if terminal_price <= 0:
            raise ValueError("terminal_price must be positive")

        if self.side == "put":
            converted = terminal_price < self.strike
            if converted:
                settlement = (self.notional_quote + self.coupon_quote) * terminal_price / self.strike
            else:
                settlement = self.notional_quote + self.coupon_quote
            benchmark = self.notional_quote
            return ProductResult(terminal_price, settlement, benchmark, converted)

        coupon_base = self.base_quantity * self.apr * self.tenor_years
        converted = terminal_price > self.strike
        if converted:
            settlement = (self.base_quantity + coupon_base) * self.strike
        else:
            settlement = (self.base_quantity + coupon_base) * terminal_price
        benchmark = self.base_quantity * terminal_price
        return ProductResult(terminal_price, settlement, benchmark, converted)

    def evaluate_many(self, terminal_prices: list[float]) -> list[ProductResult]:
        return [self.evaluate(price) for price in terminal_prices]

