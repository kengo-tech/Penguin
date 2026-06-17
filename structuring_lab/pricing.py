from __future__ import annotations

from math import erf, exp, log, sqrt


def normal_cdf(x: float) -> float:
    return 0.5 * (1.0 + erf(x / sqrt(2.0)))


def black_scholes_price(
    spot: float,
    strike: float,
    tenor_years: float,
    volatility: float,
    rate: float = 0.0,
    option_type: str = "put",
) -> float:
    """Return European option price for a non-dividend asset."""

    if spot <= 0 or strike <= 0:
        raise ValueError("spot and strike must be positive")
    if tenor_years <= 0:
        if option_type == "call":
            return max(spot - strike, 0.0)
        if option_type == "put":
            return max(strike - spot, 0.0)
        raise ValueError("option_type must be call or put")
    if volatility <= 0:
        forward_intrinsic = spot - strike * exp(-rate * tenor_years)
        if option_type == "call":
            return max(forward_intrinsic, 0.0)
        if option_type == "put":
            return max(-forward_intrinsic, 0.0)
        raise ValueError("option_type must be call or put")

    sigma_sqrt_t = volatility * sqrt(tenor_years)
    d1 = (log(spot / strike) + (rate + 0.5 * volatility**2) * tenor_years) / sigma_sqrt_t
    d2 = d1 - sigma_sqrt_t

    if option_type == "call":
        return spot * normal_cdf(d1) - strike * exp(-rate * tenor_years) * normal_cdf(d2)
    if option_type == "put":
        return strike * exp(-rate * tenor_years) * normal_cdf(-d2) - spot * normal_cdf(-d1)
    raise ValueError("option_type must be call or put")


def fair_apr_from_option_premium(
    option_premium: float,
    notional: float,
    tenor_days: int,
    participation: float = 1.0,
) -> float:
    if notional <= 0:
        raise ValueError("notional must be positive")
    if tenor_days <= 0:
        raise ValueError("tenor_days must be positive")
    return option_premium * participation / notional * 365.0 / tenor_days

