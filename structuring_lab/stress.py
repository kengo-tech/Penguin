from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from math import log, sqrt
from statistics import mean

from structuring_lab.binance import Kline
from structuring_lab.macro import RatePoint, forward_fill_rates, rate_on_or_before
from structuring_lab.risk import percentile


@dataclass(frozen=True)
class StressDay:
    date: date
    close: float
    quote_volume: float
    daily_return: float
    range_pct: float
    rolling_volatility: float | None
    rolling_drawdown: float | None
    amihud_illiq: float
    t_bill_3m: float | None
    fed_funds: float | None
    stress_score: float | None
    liquidity_constrained: bool


@dataclass(frozen=True)
class StressYearSummary:
    year: int
    observations: int
    btc_return: float
    max_drawdown: float
    liquidity_days: int
    liquidity_day_ratio: float
    liquidity_period_mdd: float | None
    average_stress_score: float
    average_rolling_volatility: float
    average_range_pct: float
    average_amihud_illiq: float
    average_t_bill_3m: float | None
    average_fed_funds: float | None
    max_t_bill_3m: float | None


def max_drawdown(prices: list[float]) -> float:
    if not prices:
        raise ValueError("prices must not be empty")
    peak = prices[0]
    worst = 0.0
    for price in prices:
        peak = max(peak, price)
        worst = min(worst, price / peak - 1.0)
    return worst


def _rolling_max_drawdown(prices: list[float], window: int) -> list[float | None]:
    output: list[float | None] = []
    for index in range(len(prices)):
        if index + 1 < window:
            output.append(None)
        else:
            output.append(max_drawdown(prices[index + 1 - window : index + 1]))
    return output


def _rolling_volatility(returns: list[float], window: int) -> list[float | None]:
    output: list[float | None] = []
    for index in range(len(returns)):
        if index + 1 < window:
            output.append(None)
            continue
        sample = returns[index + 1 - window : index + 1]
        sample_mean = mean(sample)
        variance = sum((value - sample_mean) ** 2 for value in sample) / (len(sample) - 1)
        output.append(sqrt(variance) * sqrt(365.0))
    return output


def _z_scores(values: list[float | None]) -> list[float | None]:
    clean = [value for value in values if value is not None]
    if len(clean) < 2:
        return [None for _ in values]
    center = mean(clean)
    variance = sum((value - center) ** 2 for value in clean) / (len(clean) - 1)
    scale = sqrt(variance)
    if scale == 0:
        return [0.0 if value is not None else None for value in values]
    return [(value - center) / scale if value is not None else None for value in values]


def build_stress_days(
    klines: list[Kline],
    t_bill_3m: list[RatePoint],
    fed_funds: list[RatePoint],
    rolling_window: int = 30,
    stress_percentile: float = 90.0,
) -> list[StressDay]:
    rows = sorted(klines, key=lambda row: row.open_time)
    if len(rows) < rolling_window + 1:
        raise ValueError("not enough klines for stress feature window")

    closes = [row.close for row in rows]
    returns = [0.0] + [log(closes[index] / closes[index - 1]) for index in range(1, len(closes))]
    ranges = [(row.high - row.low) / row.close for row in rows]
    amihud = [abs(returns[index]) / max(rows[index].quote_volume / 1_000_000.0, 1e-12) for index in range(len(rows))]
    rolling_vol = _rolling_volatility(returns, rolling_window)
    rolling_mdd = _rolling_max_drawdown(closes, rolling_window)

    range_z = _z_scores(ranges)
    amihud_z = _z_scores(amihud)
    vol_z = _z_scores(rolling_vol)
    mdd_z = _z_scores([abs(value) if value is not None else None for value in rolling_mdd])

    raw_scores: list[float | None] = []
    for values in zip(range_z, amihud_z, vol_z, mdd_z):
        if any(value is None for value in values):
            raw_scores.append(None)
        else:
            raw_scores.append(sum(value or 0.0 for value in values) / 4.0)

    score_threshold = percentile([score for score in raw_scores if score is not None], stress_percentile)
    t_bill_by_date = forward_fill_rates(t_bill_3m)
    fed_funds_by_date = forward_fill_rates(fed_funds)

    days: list[StressDay] = []
    for index, row in enumerate(rows):
        row_date = row.open_time.date()
        score = raw_scores[index]
        days.append(
            StressDay(
                date=row_date,
                close=row.close,
                quote_volume=row.quote_volume,
                daily_return=returns[index],
                range_pct=ranges[index],
                rolling_volatility=rolling_vol[index],
                rolling_drawdown=rolling_mdd[index],
                amihud_illiq=amihud[index],
                t_bill_3m=rate_on_or_before(t_bill_by_date, row_date),
                fed_funds=rate_on_or_before(fed_funds_by_date, row_date),
                stress_score=score,
                liquidity_constrained=score is not None and score >= score_threshold,
            )
        )
    return days


def summarize_stress_by_year(days: list[StressDay], start_year: int, end_year: int) -> list[StressYearSummary]:
    summaries: list[StressYearSummary] = []
    for year in range(start_year, end_year + 1):
        year_days = [day for day in days if day.date.year == year]
        if not year_days:
            continue
        clean_scores = [day.stress_score for day in year_days if day.stress_score is not None]
        clean_vols = [day.rolling_volatility for day in year_days if day.rolling_volatility is not None]
        t_bills = [day.t_bill_3m for day in year_days if day.t_bill_3m is not None]
        fed_rates = [day.fed_funds for day in year_days if day.fed_funds is not None]
        liquidity_days = [day for day in year_days if day.liquidity_constrained]

        summaries.append(
            StressYearSummary(
                year=year,
                observations=len(year_days),
                btc_return=year_days[-1].close / year_days[0].close - 1.0,
                max_drawdown=max_drawdown([day.close for day in year_days]),
                liquidity_days=len(liquidity_days),
                liquidity_day_ratio=len(liquidity_days) / len(year_days),
                liquidity_period_mdd=max_drawdown([day.close for day in liquidity_days]) if len(liquidity_days) >= 2 else None,
                average_stress_score=mean(clean_scores) if clean_scores else 0.0,
                average_rolling_volatility=mean(clean_vols) if clean_vols else 0.0,
                average_range_pct=mean(day.range_pct for day in year_days),
                average_amihud_illiq=mean(day.amihud_illiq for day in year_days),
                average_t_bill_3m=mean(t_bills) if t_bills else None,
                average_fed_funds=mean(fed_rates) if fed_rates else None,
                max_t_bill_3m=max(t_bills) if t_bills else None,
            )
        )
    return summaries

