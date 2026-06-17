from __future__ import annotations

from dataclasses import dataclass
from math import exp, log, sqrt
import random
from statistics import mean, median, stdev


@dataclass(frozen=True)
class RiskSummary:
    initial_value: float
    expected_value: float
    expected_return: float
    median_value: float
    probability_of_loss: float
    var_95: float
    cvar_95: float
    worst_value: float
    best_value: float
    conversion_probability: float | None = None
    expected_benchmark_gap: float | None = None


def percentile(values: list[float], p: float) -> float:
    if not values:
        raise ValueError("values must not be empty")
    if not 0 <= p <= 100:
        raise ValueError("p must be between 0 and 100")
    ordered = sorted(values)
    if len(ordered) == 1:
        return ordered[0]
    rank = (len(ordered) - 1) * p / 100
    low = int(rank)
    high = min(low + 1, len(ordered) - 1)
    weight = rank - low
    return ordered[low] * (1 - weight) + ordered[high] * weight


def log_returns(prices: list[float]) -> list[float]:
    if len(prices) < 2:
        raise ValueError("at least two prices are required")
    return [log(prices[i] / prices[i - 1]) for i in range(1, len(prices))]


def annualized_volatility(daily_log_returns: list[float]) -> float:
    if len(daily_log_returns) < 2:
        return 0.0
    return stdev(daily_log_returns) * sqrt(365.0)


def annualized_drift(daily_log_returns: list[float]) -> float:
    if not daily_log_returns:
        return 0.0
    return mean(daily_log_returns) * 365.0


def simulate_gbm_terminal_prices(
    spot: float,
    annual_drift: float,
    annual_volatility: float,
    tenor_days: int,
    paths: int = 10000,
    seed: int | None = 7,
) -> list[float]:
    if spot <= 0:
        raise ValueError("spot must be positive")
    if tenor_days <= 0 or paths <= 0:
        raise ValueError("tenor_days and paths must be positive")

    rng = random.Random(seed)
    dt = tenor_days / 365.0
    drift_term = (annual_drift - 0.5 * annual_volatility**2) * dt
    vol_term = annual_volatility * sqrt(dt)
    return [spot * exp(drift_term + vol_term * rng.gauss(0.0, 1.0)) for _ in range(paths)]


def summarize_values(
    values: list[float],
    initial_value: float,
    conversions: list[bool] | None = None,
    benchmark_gaps: list[float] | None = None,
) -> RiskSummary:
    if not values:
        raise ValueError("values must not be empty")
    if initial_value <= 0:
        raise ValueError("initial_value must be positive")

    losses = [initial_value - value for value in values]
    var_95 = percentile(losses, 95)
    tail_losses = [loss for loss in losses if loss >= var_95]
    conversion_probability = None
    if conversions is not None:
        conversion_probability = sum(conversions) / len(conversions)

    expected_benchmark_gap = None
    if benchmark_gaps is not None:
        expected_benchmark_gap = mean(benchmark_gaps)

    expected_value = mean(values)
    return RiskSummary(
        initial_value=initial_value,
        expected_value=expected_value,
        expected_return=expected_value / initial_value - 1.0,
        median_value=median(values),
        probability_of_loss=sum(value < initial_value for value in values) / len(values),
        var_95=var_95,
        cvar_95=mean(tail_losses),
        worst_value=min(values),
        best_value=max(values),
        conversion_probability=conversion_probability,
        expected_benchmark_gap=expected_benchmark_gap,
    )

