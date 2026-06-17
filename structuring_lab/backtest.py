from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from statistics import mean

from structuring_lab.binance import Kline
from structuring_lab.products import DualCurrencyInvestment
from structuring_lab.risk import RiskSummary, annualized_volatility, log_returns, summarize_values


@dataclass(frozen=True)
class YearlyDciBacktest:
    year: int
    observations: int
    first_entry: datetime
    last_entry: datetime
    start_spot: float
    end_spot: float
    buy_and_hold_return: float
    historical_volatility: float
    summary: RiskSummary


def rolling_dci_backtest_by_year(
    klines: list[Kline],
    start_year: int,
    end_year: int,
    side: str,
    strike_moneyness: float,
    notional: float,
    apr: float,
    tenor_days: int,
) -> list[YearlyDciBacktest]:
    """Run realized rolling DCI backtests grouped by entry calendar year."""

    if tenor_days <= 0:
        raise ValueError("tenor_days must be positive")
    if start_year > end_year:
        raise ValueError("start_year must be less than or equal to end_year")
    if len(klines) <= tenor_days:
        raise ValueError("not enough klines for the requested tenor")

    rows = sorted(klines, key=lambda row: row.open_time)
    output: list[YearlyDciBacktest] = []

    for year in range(start_year, end_year + 1):
        entry_indices = [
            index
            for index in range(0, len(rows) - tenor_days)
            if rows[index].open_time.year == year
        ]
        if not entry_indices:
            continue

        values: list[float] = []
        conversions: list[bool] = []
        benchmark_gaps: list[float] = []

        for index in entry_indices:
            entry = rows[index]
            terminal = rows[index + tenor_days]
            product = DualCurrencyInvestment(
                spot=entry.close,
                strike=entry.close * strike_moneyness,
                notional_quote=notional,
                apr=apr,
                tenor_days=tenor_days,
                side=side,
            )
            result = product.evaluate(terminal.close)
            values.append(result.settlement_value_quote)
            conversions.append(result.converted)
            benchmark_gaps.append(result.benchmark_gap)

        year_rows = [rows[index] for index in entry_indices]
        year_prices = [row.close for row in year_rows]
        year_returns = log_returns(year_prices) if len(year_prices) > 1 else []
        summary = summarize_values(
            values,
            initial_value=notional,
            conversions=conversions,
            benchmark_gaps=benchmark_gaps,
        )
        output.append(
            YearlyDciBacktest(
                year=year,
                observations=len(entry_indices),
                first_entry=year_rows[0].open_time,
                last_entry=year_rows[-1].open_time,
                start_spot=year_rows[0].close,
                end_spot=year_rows[-1].close,
                buy_and_hold_return=year_rows[-1].close / year_rows[0].close - 1.0,
                historical_volatility=annualized_volatility(year_returns),
                summary=summary,
            )
        )

    return output


def average_expected_return(results: list[YearlyDciBacktest]) -> float:
    if not results:
        raise ValueError("results must not be empty")
    return mean(result.summary.expected_return for result in results)

