from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
import csv
from io import StringIO
from urllib.request import Request, urlopen


FRED_CSV_URL = "https://fred.stlouisfed.org/graph/fredgraph.csv"


@dataclass(frozen=True)
class RatePoint:
    date: date
    value: float


def fetch_fred_series(series_id: str, timeout: int = 15) -> list[RatePoint]:
    """Fetch a FRED series through the public graph CSV endpoint."""

    url = f"{FRED_CSV_URL}?id={series_id.upper()}"
    request = Request(url, headers={"User-Agent": "crypto-structuring-lab/0.1"})
    with urlopen(request, timeout=timeout) as response:
        text = response.read().decode("utf-8")

    rows: list[RatePoint] = []
    reader = csv.DictReader(StringIO(text))
    for row in reader:
        raw_date = row.get("observation_date")
        raw_value = row.get(series_id.upper())
        if not raw_date or not raw_value or raw_value == ".":
            continue
        rows.append(
            RatePoint(
                date=datetime.strptime(raw_date, "%Y-%m-%d").date(),
                value=float(raw_value) / 100.0,
            )
        )
    return rows


def forward_fill_rates(points: list[RatePoint]) -> dict[date, float]:
    return {point.date: point.value for point in sorted(points, key=lambda point: point.date)}


def rate_on_or_before(rate_by_date: dict[date, float], target: date) -> float | None:
    if target in rate_by_date:
        return rate_by_date[target]
    eligible = [item_date for item_date in rate_by_date if item_date <= target]
    if not eligible:
        return None
    return rate_by_date[max(eligible)]

