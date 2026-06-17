from __future__ import annotations

import argparse
from datetime import datetime, timezone
from statistics import mean

from structuring_lab.backtest import rolling_dci_backtest_by_year
from structuring_lab.binance import PublicBinanceFuturesClient
from structuring_lab.pricing import black_scholes_price, fair_apr_from_option_premium
from structuring_lab.products import DualCurrencyInvestment
from structuring_lab.risk import (
    annualized_drift,
    annualized_volatility,
    log_returns,
    simulate_gbm_terminal_prices,
    summarize_funding_rates,
    summarize_values,
)


def _pct(value: float, decimals: int = 2) -> str:
    return f"{value * 100:,.{decimals}f}%"


def _money(value: float) -> str:
    return f"{value:,.2f}"


def _utc_date(year: int, month: int = 1, day: int = 1) -> datetime:
    return datetime(year, month, day, tzinfo=timezone.utc)


def _offline_prices(spot: float) -> list[float]:
    returns = simulate_gbm_terminal_prices(
        spot=spot,
        annual_drift=0.05,
        annual_volatility=0.65,
        tenor_days=1,
        paths=366,
        seed=11,
    )
    prices = [spot]
    for terminal in returns[1:]:
        prices.append(max(1.0, prices[-1] * terminal / spot))
    return prices


def run_dci(args: argparse.Namespace) -> None:
    if args.offline_demo:
        prices = _offline_prices(args.spot)
        data_source = "offline demo"
    else:
        client = PublicBinanceFuturesClient()
        klines = client.klines(args.symbol, interval=args.interval, limit=args.lookback)
        prices = [row.close for row in klines]
        data_source = f"Binance USD-M Futures {args.symbol}"

    spot = prices[-1] if args.spot is None else args.spot
    strike = args.strike
    if strike is None:
        strike = spot * args.strike_moneyness

    returns = log_returns(prices)
    drift = annualized_drift(returns) if args.use_historical_drift else 0.0
    volatility = annualized_volatility(returns)
    terminal_prices = simulate_gbm_terminal_prices(
        spot=spot,
        annual_drift=drift,
        annual_volatility=volatility,
        tenor_days=args.tenor_days,
        paths=args.paths,
        seed=args.seed,
    )

    product = DualCurrencyInvestment(
        spot=spot,
        strike=strike,
        notional_quote=args.notional,
        apr=args.apr,
        tenor_days=args.tenor_days,
        side=args.side,
    )
    results = product.evaluate_many(terminal_prices)
    values = [result.settlement_value_quote for result in results]
    summary = summarize_values(
        values,
        initial_value=args.notional,
        conversions=[result.converted for result in results],
        benchmark_gaps=[result.benchmark_gap for result in results],
    )

    option_type = "put" if args.side == "put" else "call"
    option_unit_price = black_scholes_price(
        spot=spot,
        strike=strike,
        tenor_years=args.tenor_days / 365.0,
        volatility=volatility,
        rate=args.rate,
        option_type=option_type,
    )
    option_notional_price = option_unit_price * (args.notional / strike if args.side == "put" else args.notional / spot)
    fair_apr = fair_apr_from_option_premium(option_notional_price, args.notional, args.tenor_days)

    print("Crypto Derivatives Structuring Lab")
    print("----------------------------------")
    print(f"Data source: {data_source}")
    print(f"Product: Dual Currency Investment ({args.side})")
    print(f"Spot: {_money(spot)}")
    print(f"Strike: {_money(strike)}")
    print(f"Notional quote: {_money(args.notional)}")
    print(f"Tenor: {args.tenor_days} days")
    print(f"Client APR: {_pct(args.apr)}")
    print(f"Historical annualized volatility: {_pct(volatility)}")
    print(f"Simulation drift: {_pct(drift)}")
    print("")
    print("Risk summary")
    print(f"Expected value: {_money(summary.expected_value)}")
    print(f"Expected return: {_pct(summary.expected_return)}")
    print(f"Median value: {_money(summary.median_value)}")
    print(f"Probability of loss: {_pct(summary.probability_of_loss)}")
    print(f"Conversion probability: {_pct(summary.conversion_probability or 0.0)}")
    print(f"VaR 95 loss: {_money(summary.var_95)}")
    print(f"CVaR 95 loss: {_money(summary.cvar_95)}")
    print(f"Worst / best value: {_money(summary.worst_value)} / {_money(summary.best_value)}")
    print(f"Expected benchmark gap: {_money(summary.expected_benchmark_gap or 0.0)}")
    print("")
    print("Option reference")
    print(f"BS {option_type} premium on product quantity: {_money(option_notional_price)}")
    print(f"BS-implied fair APR before margin/share split: {_pct(fair_apr)}")
    print(f"Average simulated terminal price: {_money(mean(terminal_prices))}")


def run_funding(args: argparse.Namespace) -> None:
    client = PublicBinanceFuturesClient()
    rows = client.funding_rates(args.symbol, limit=args.limit)
    rates = [row.funding_rate for row in rows]
    summary = summarize_funding_rates(rates)

    print("Crypto Derivatives Structuring Lab")
    print("----------------------------------")
    print(f"Data source: Binance USD-M Futures funding rates {args.symbol}")
    print(f"First funding time: {rows[0].funding_time.isoformat()}")
    print(f"Last funding time: {rows[-1].funding_time.isoformat()}")
    print(f"Observations: {summary.observations}")
    print("")
    print("Funding summary")
    print(f"Mean funding rate per event: {_pct(summary.mean_rate, 4)}")
    print(f"Median funding rate per event: {_pct(summary.median_rate, 4)}")
    print(f"Std funding rate per event: {_pct(summary.stdev_rate, 4)}")
    print(f"Positive funding probability: {_pct(summary.positive_probability)}")
    print(f"Annualized mean funding: {_pct(summary.annualized_mean_rate)}")
    print(f"Cumulative simple funding over sample: {_pct(summary.cumulative_simple_return)}")
    print(f"Worst / best event: {_pct(summary.worst_rate, 4)} / {_pct(summary.best_rate, 4)}")


def run_dci_years(args: argparse.Namespace) -> None:
    client = PublicBinanceFuturesClient()
    fetch_start = _utc_date(args.start_year)
    fetch_end_year = args.end_year + 1
    fetch_end = _utc_date(fetch_end_year)
    rows = client.klines_range(args.symbol, start=fetch_start, end=fetch_end, interval="1d")
    results = rolling_dci_backtest_by_year(
        rows,
        start_year=args.start_year,
        end_year=args.end_year,
        side=args.side,
        strike_moneyness=args.strike_moneyness,
        notional=args.notional,
        apr=args.apr,
        tenor_days=args.tenor_days,
    )

    print("Crypto Derivatives Structuring Lab")
    print("----------------------------------")
    print(f"Data source: Binance USD-M Futures daily klines {args.symbol}")
    print(f"Backtest: rolling {args.tenor_days}-day DCI by entry year")
    print(f"Side: {args.side}")
    print(f"Strike moneyness: {_pct(args.strike_moneyness - 1.0)} vs spot")
    print(f"Client APR: {_pct(args.apr)}")
    print(f"Notional quote: {_money(args.notional)}")
    print("")
    header = (
        "Year  Obs  Entry start  Entry last  BTC return  Vol      "
        "DCI return  Loss prob  Conv prob  VaR95 loss  CVaR95 loss  Bench gap"
    )
    print(header)
    print("-" * len(header))
    for result in results:
        summary = result.summary
        print(
            f"{result.year:<5} "
            f"{result.observations:>3} "
            f"{_money(result.start_spot):>11} "
            f"{_money(result.end_spot):>10} "
            f"{_pct(result.buy_and_hold_return):>11} "
            f"{_pct(result.historical_volatility):>8} "
            f"{_pct(summary.expected_return):>11} "
            f"{_pct(summary.probability_of_loss):>10} "
            f"{_pct(summary.conversion_probability or 0.0):>10} "
            f"{_money(summary.var_95):>11} "
            f"{_money(summary.cvar_95):>12} "
            f"{_money(summary.expected_benchmark_gap or 0.0):>10}"
        )


def run_dci_tenors(args: argparse.Namespace) -> None:
    client = PublicBinanceFuturesClient()
    fetch_start = _utc_date(args.start_year)
    fetch_end = _utc_date(args.end_year + 1)
    rows = client.klines_range(args.symbol, start=fetch_start, end=fetch_end, interval="1d")

    print("Crypto Derivatives Structuring Lab")
    print("----------------------------------")
    print(f"Data source: Binance USD-M Futures daily klines {args.symbol}")
    print(f"Backtest: rolling DCI by entry year and tenor")
    print(f"Side: {args.side}")
    print(f"Strike moneyness: {_pct(args.strike_moneyness - 1.0)} vs spot")
    print(f"Client APR: {_pct(args.apr)}")
    print(f"Notional quote: {_money(args.notional)}")
    print("")
    header = (
        "Tenor  Year  Obs  BTC return  Vol      DCI return  "
        "Loss prob  Conv prob  VaR95 loss  CVaR95 loss  Bench gap"
    )
    print(header)
    print("-" * len(header))

    for tenor_days in args.tenor_days:
        results = rolling_dci_backtest_by_year(
            rows,
            start_year=args.start_year,
            end_year=args.end_year,
            side=args.side,
            strike_moneyness=args.strike_moneyness,
            notional=args.notional,
            apr=args.apr,
            tenor_days=tenor_days,
        )
        for result in results:
            summary = result.summary
            print(
                f"{tenor_days:>5} "
                f"{result.year:<5} "
                f"{result.observations:>3} "
                f"{_pct(result.buy_and_hold_return):>11} "
                f"{_pct(result.historical_volatility):>8} "
                f"{_pct(summary.expected_return):>11} "
                f"{_pct(summary.probability_of_loss):>10} "
                f"{_pct(summary.conversion_probability or 0.0):>10} "
                f"{_money(summary.var_95):>11} "
                f"{_money(summary.cvar_95):>12} "
                f"{_money(summary.expected_benchmark_gap or 0.0):>10}"
            )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Crypto derivative structuring simulations.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    dci = subparsers.add_parser("dci", help="simulate a Dual Currency Investment")
    dci.add_argument("--symbol", default="BTCUSDT")
    dci.add_argument("--interval", default="1d")
    dci.add_argument("--lookback", type=int, default=365)
    dci.add_argument("--offline-demo", action="store_true")
    dci.add_argument("--side", choices=["put", "call"], default="put")
    dci.add_argument("--spot", type=float)
    dci.add_argument("--strike", type=float)
    dci.add_argument("--strike-moneyness", type=float, default=0.9)
    dci.add_argument("--notional", type=float, default=100000.0)
    dci.add_argument("--apr", type=float, default=0.12)
    dci.add_argument("--tenor-days", type=int, default=30)
    dci.add_argument("--paths", type=int, default=10000)
    dci.add_argument("--seed", type=int, default=7)
    dci.add_argument("--rate", type=float, default=0.0)
    dci.add_argument("--use-historical-drift", action="store_true")
    dci.set_defaults(func=run_dci)

    funding = subparsers.add_parser("funding", help="summarize Binance funding rates")
    funding.add_argument("--symbol", default="BTCUSDT")
    funding.add_argument("--limit", type=int, default=1000)
    funding.set_defaults(func=run_funding)

    years = subparsers.add_parser("dci-years", help="realized rolling DCI backtest by calendar year")
    years.add_argument("--symbol", default="BTCUSDT")
    years.add_argument("--start-year", type=int, default=2020)
    years.add_argument("--end-year", type=int, default=2026)
    years.add_argument("--side", choices=["put", "call"], default="put")
    years.add_argument("--strike-moneyness", type=float, default=0.9)
    years.add_argument("--notional", type=float, default=100000.0)
    years.add_argument("--apr", type=float, default=0.12)
    years.add_argument("--tenor-days", type=int, default=30)
    years.set_defaults(func=run_dci_years)

    tenors = subparsers.add_parser("dci-tenors", help="compare realized rolling DCI backtests across tenors")
    tenors.add_argument("--symbol", default="BTCUSDT")
    tenors.add_argument("--start-year", type=int, default=2020)
    tenors.add_argument("--end-year", type=int, default=2026)
    tenors.add_argument("--side", choices=["put", "call"], default="put")
    tenors.add_argument("--strike-moneyness", type=float, default=0.9)
    tenors.add_argument("--notional", type=float, default=100000.0)
    tenors.add_argument("--apr", type=float, default=0.12)
    tenors.add_argument("--tenor-days", nargs="+", type=int, default=[90, 180, 270, 365])
    tenors.set_defaults(func=run_dci_tenors)
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
