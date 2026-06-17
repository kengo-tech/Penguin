# Liquidity-Stress Drawdown Events

Execution date: 2026-06-17

Data sources:

- Binance USD-M Futures daily `BTCUSDT` klines
- FRED `DGS3MO`: 3-Month Treasury Constant Maturity Rate
- FRED `FEDFUNDS`: Effective Federal Funds Rate

Command:

```powershell
python -m structuring_lab.cli stress-events --symbol BTCUSDT --start-year 2020 --end-year 2026 --window 30 --stress-percentile 90 --max-gap-days 7 --min-stress-days 2 --min-drawdown -0.10 --top 12
```

## Method

This analysis identifies liquidity-stress drawdown episodes using market-data proxies rather than order-book data.

First, each day receives a stress score based on:

- intraday range: `(high - low) / close`
- 30-day realized volatility
- 30-day rolling max drawdown
- Amihud-style illiquidity: `abs(return) / quote_volume_in_millions`

Then, days in the top 10% of stress scores are marked as liquidity-constrained days. Nearby stress days are grouped into one event if the gap between stress days is seven days or less. Events are kept when they have at least two stress days and either a meaningful drawdown or a negative event return.

This is a liquidity-stress proxy. It does not prove that liquidity was the sole cause of the decline. It identifies periods where price decline, volatility, range expansion, and volume-adjusted price movement were jointly elevated.

## Detected Events

| Rank | Start | End | Days | Stress Days | Return | MDD | Peak Score | Vol | Range | Illiq | 3M Bill | FedFunds |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 2020-02-15 | 2020-04-29 | 75 | 48 | -11.40% | -53.17% | 12.42 | 121.55% | 8.04% | 0.000016 | 0.48% | 0.60% |
| 2 | 2021-05-05 | 2021-07-01 | 58 | 46 | -41.75% | -46.43% | 3.61 | 103.03% | 9.77% | 0.000002 | 0.03% | 0.07% |
| 3 | 2021-01-04 | 2021-03-04 | 60 | 38 | 51.06% | -25.24% | 2.21 | 96.62% | 9.81% | 0.000003 | 0.06% | 0.08% |
| 4 | 2021-11-26 | 2021-12-13 | 18 | 5 | -13.16% | -19.28% | 2.05 | 66.79% | 7.37% | 0.000002 | 0.06% | 0.08% |
| 5 | 2022-06-13 | 2022-07-11 | 29 | 28 | -11.20% | -15.99% | 2.05 | 91.50% | 7.49% | 0.000002 | 1.77% | 1.39% |
| 6 | 2022-02-24 | 2022-03-09 | 14 | 4 | 9.45% | -14.48% | 1.27 | 76.30% | 7.19% | 0.000002 | 0.35% | 0.16% |
| 7 | 2020-05-07 | 2020-06-02 | 27 | 10 | -4.80% | -14.35% | 1.73 | 77.38% | 6.36% | 0.000010 | 0.13% | 0.05% |
| 8 | 2022-11-08 | 2022-11-14 | 7 | 5 | -10.41% | -14.18% | 1.60 | 75.63% | 11.17% | 0.000003 | 4.29% | 3.78% |
| 9 | 2021-03-13 | 2021-03-22 | 10 | 3 | -11.65% | -11.65% | 0.94 | 83.00% | 6.99% | 0.000002 | 0.02% | 0.07% |
| 10 | 2022-09-09 | 2022-09-13 | 5 | 2 | -5.57% | -9.93% | 1.20 | 67.01% | 7.21% | 0.000002 | 3.14% | 2.56% |
| 11 | 2022-05-09 | 2022-06-01 | 24 | 12 | -0.86% | -8.62% | 1.34 | 76.83% | 6.79% | 0.000002 | 1.04% | 0.79% |

## Main Episodes

### 1. February-April 2020: broad liquidation shock

This is the largest liquidity-stress event in the sample. The event max drawdown is -53.17%, the average 30-day realized volatility is 121.55%, and the Amihud-style illiquidity measure is the highest among the listed episodes.

Interpretation for structured products:

- Hedging can become discontinuous because prices gap and intraday ranges expand.
- Stop-loss or delta-hedging rules become less reliable.
- For put-side DCI, conversion risk becomes acute.
- For lending or Stable-Return products, early redemption pressure and collateral liquidation risk become central.

### 2. May-July 2021: high-volatility deleveraging

This period shows a -41.75% event return, -46.43% max drawdown, and a 103.03% average realized volatility. The stress-day count is also high at 46 days.

Interpretation for structured products:

- A 10% downside buffer is not enough when the market enters a multi-week deleveraging phase.
- High APR can be overwhelmed by the mark-to-market effect of conversion.
- If the product assumes stable liquidity for hedging, the assumption should be stress-tested.

### 3. January-March 2021: volatile rally with large intra-period drawdown

The final event return is positive, but the max drawdown is still -25.24%. This matters because liquidity stress is not only a bear-market feature. Fast rallies can also produce unstable order flow, forced liquidations, and large interim drawdowns.

Interpretation for structured products:

- Call-side DCI can be converted quickly in strong upside regimes.
- A client may see positive product P&L while still suffering large opportunity cost versus BTC holding.
- Product risk should include benchmark gap, not only absolute return.

### 4. June-July 2022 and November 2022: crypto credit and exchange-liquidity stress

The June-July 2022 event appears after the May 2022 stablecoin and lending-market stress, while the November 2022 event coincides with the FTX crisis. The November event has the highest average range in the table at 11.17%, despite lasting only seven days.

Interpretation for structured products:

- Counterparty, exchange, and lending-platform risk can become more important than the vanilla option payoff.
- A product can be theoretically hedged but practically hard to unwind if exchange liquidity or withdrawals are constrained.
- For client communication, this is where "no secondary market" and "early redemption may be unavailable" must be explicit.

## Feature Pattern

The strongest liquidity-stress drawdowns share several features:

- high realized volatility, often above 75%-100% annualized;
- daily range expansion above 7%-10%;
- clustered stress days rather than one isolated outlier;
- large rolling drawdowns;
- in 2022, rising short-term rates added a higher hurdle rate for any yield product.

## Risk Management Tests To Add

For DCI:

- reprice the product under a forced conversion scenario;
- shock BTC by the event max drawdown;
- compare coupon earned versus mark-to-market loss;
- compute benchmark gap during rally stress events.

For Stable-Return and lending-based products:

- assume no early redemption during stress events;
- haircut collateral and widen liquidation slippage;
- increase funding cost by the Treasury-bill rate plus a lending spread;
- model exchange/counterparty failure as a separate jump-to-loss scenario;
- test whether promised APR survives a 30- to 60-day liquidity freeze.

## Sales Framing

A careful client explanation should say:

> Historical stress events show that the main risk is not only price direction. In liquidity-constrained declines, volatility, drawdown, execution cost, funding cost, and redemption limits can arrive together. The product should be evaluated against these stress windows, not only against average returns or headline APR.

## References

- Binance USD-M Futures kline data: `GET /fapi/v1/klines`
- FRED `DGS3MO`: 3-month Treasury yield
- FRED `FEDFUNDS`: effective Fed funds rate
- BIS Bulletin No. 69 discusses crypto shocks after Terra/Luna and FTX, and notes increased trading activity and losses around these episodes.

