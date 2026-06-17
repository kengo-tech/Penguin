from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import json
from typing import Any
from urllib.parse import urlencode
from urllib.request import Request, urlopen


BINANCE_USDM_FUTURES_BASE_URL = "https://fapi.binance.com"


@dataclass(frozen=True)
class Kline:
    open_time: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float
    close_time: datetime
    quote_volume: float
    trades: int


@dataclass(frozen=True)
class FundingRate:
    symbol: str
    funding_time: datetime
    funding_rate: float
    mark_price: float


def _dt_from_ms(value: int) -> datetime:
    return datetime.fromtimestamp(value / 1000, tz=timezone.utc)


class PublicBinanceFuturesClient:
    """Small client for Binance USD-M Futures public market data."""

    def __init__(self, base_url: str = BINANCE_USDM_FUTURES_BASE_URL, timeout: int = 15):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def _get(self, path: str, params: dict[str, Any] | None = None) -> Any:
        query = f"?{urlencode(params)}" if params else ""
        request = Request(
            f"{self.base_url}{path}{query}",
            headers={"User-Agent": "crypto-structuring-lab/0.1"},
        )
        with urlopen(request, timeout=self.timeout) as response:
            return json.loads(response.read().decode("utf-8"))

    def exchange_info(self) -> dict[str, Any]:
        return self._get("/fapi/v1/exchangeInfo")

    def klines(
        self,
        symbol: str,
        interval: str = "1d",
        limit: int = 365,
        start_time_ms: int | None = None,
        end_time_ms: int | None = None,
    ) -> list[Kline]:
        params: dict[str, Any] = {
            "symbol": symbol.upper(),
            "interval": interval,
            "limit": limit,
        }
        if start_time_ms is not None:
            params["startTime"] = start_time_ms
        if end_time_ms is not None:
            params["endTime"] = end_time_ms

        raw_rows = self._get("/fapi/v1/klines", params)
        return [
            Kline(
                open_time=_dt_from_ms(row[0]),
                open=float(row[1]),
                high=float(row[2]),
                low=float(row[3]),
                close=float(row[4]),
                volume=float(row[5]),
                close_time=_dt_from_ms(row[6]),
                quote_volume=float(row[7]),
                trades=int(row[8]),
            )
            for row in raw_rows
        ]

    def funding_rates(
        self,
        symbol: str,
        limit: int = 100,
        start_time_ms: int | None = None,
        end_time_ms: int | None = None,
    ) -> list[FundingRate]:
        params: dict[str, Any] = {"symbol": symbol.upper(), "limit": limit}
        if start_time_ms is not None:
            params["startTime"] = start_time_ms
        if end_time_ms is not None:
            params["endTime"] = end_time_ms

        raw_rows = self._get("/fapi/v1/fundingRate", params)
        return [
            FundingRate(
                symbol=row["symbol"],
                funding_time=_dt_from_ms(row["fundingTime"]),
                funding_rate=float(row["fundingRate"]),
                mark_price=float(row["markPrice"]),
            )
            for row in raw_rows
        ]

