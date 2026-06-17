# Yearly Backtest: BTCUSDT DCI from 2020 to 2026

Execution date: 2026-06-17

Data source:

- Binance USD-M Futures daily `BTCUSDT` klines
- Entry frequency: daily rolling entries
- Tenor: 30 days
- Notional: 100,000 USDT
- Client APR: 12.00%

Important note:

2026 is a partial-year result. The backtest only includes entries with a realized 30-day terminal price available in the downloaded Binance data. With data available through 2026-06-17, the latest eligible 30-day entry is around 2026-05-18.

## Method

For each calendar year, the code assumes a new DCI is entered every day.

For each entry:

1. Use that day's BTCUSDT close as spot.
2. Set strike from moneyness.
3. Hold the DCI for 30 calendar days.
4. Use the actual BTCUSDT close 30 days later as terminal price.
5. Compute realized payoff, loss, conversion, VaR, CVaR, and benchmark gap.

This is a realized historical backtest, not a Monte Carlo simulation.

## Stablecoin-Denominated DCI

Structure:

- Side: `put`
- Strike: 90% of entry spot
- Interpretation: similar to cash-secured put selling
- Client risk: BTC falls below strike and the client is converted into BTC at an unfavorable level

Command:

```powershell
python -m structuring_lab.cli dci-years --symbol BTCUSDT --start-year 2020 --end-year 2026 --side put --strike-moneyness 0.9 --notional 100000 --apr 0.12 --tenor-days 30
```

| Year | Obs | BTC Return | Vol | DCI Return | Loss Prob | Conv Prob | VaR95 Loss | CVaR95 Loss | Bench Gap |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 2020 | 366 | 302.24% | 81.96% | -1.16% | 11.48% | 12.84% | 16,785.75 | 30,765.04 | -1,161.53 |
| 2021 | 365 | 57.52% | 81.14% | -2.87% | 30.41% | 31.23% | 20,314.15 | 27,109.42 | -2,871.05 |
| 2022 | 365 | -65.33% | 64.53% | -3.52% | 36.16% | 38.08% | 20,909.10 | 24,653.36 | -3,521.65 |
| 2023 | 365 | 154.75% | 43.73% | 0.81% | 7.40% | 9.59% | 734.07 | 1,631.32 | 807.02 |
| 2024 | 366 | 111.50% | 52.66% | 0.62% | 6.83% | 8.47% | 1,682.36 | 5,311.64 | 617.52 |
| 2025 | 365 | -7.37% | 41.76% | 0.02% | 15.07% | 16.99% | 6,465.42 | 9,542.99 | 23.58 |
| 2026 | 138 | -13.33% | 52.11% | -3.76% | 34.78% | 34.78% | 18,698.29 | 20,522.13 | -3,763.69 |

Interpretation:

The stablecoin DCI performs best in years where BTC does not frequently break 10% below entry spot over the following 30 days. In this sample, 2023 and 2024 are favorable because conversion rates stay below 10%. The product performs poorly in 2021, 2022, and partial 2026 because downside moves trigger frequent conversions and large tail losses.

Sales point:

For this product, the main client question is not "Is 12% APR high?" but "How often do I get converted into BTC, and what is the realized loss when that happens?"

## BTC-Denominated DCI

Structure:

- Side: `call`
- Strike: 110% of entry spot
- Interpretation: similar to covered call selling
- Client risk: BTC rallies above strike and the client gives up upside

Command:

```powershell
python -m structuring_lab.cli dci-years --symbol BTCUSDT --start-year 2020 --end-year 2026 --side call --strike-moneyness 1.1 --notional 100000 --apr 0.12 --tenor-days 30
```

| Year | Obs | BTC Return | Vol | DCI Return | Loss Prob | Conv Prob | VaR95 Loss | CVaR95 Loss | Bench Gap |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 2020 | 366 | 302.24% | 81.96% | 3.37% | 28.69% | 57.38% | 25,107.17 | 37,688.54 | -12,169.09 |
| 2021 | 365 | 57.52% | 81.14% | -2.50% | 51.23% | 37.81% | 28,282.74 | 34,398.48 | -6,518.68 |
| 2022 | 365 | -65.33% | 64.53% | -5.24% | 56.99% | 15.89% | 28,818.19 | 32,188.02 | -833.94 |
| 2023 | 365 | 154.75% | 43.73% | 3.94% | 32.88% | 38.90% | 10,660.66 | 11,468.19 | -3,344.58 |
| 2024 | 366 | 111.50% | 52.66% | 3.51% | 33.61% | 35.25% | 11,514.12 | 14,780.48 | -4,862.13 |
| 2025 | 365 | -7.37% | 41.76% | -0.29% | 49.32% | 16.44% | 15,818.88 | 18,588.69 | -44.88 |
| 2026 | 138 | -13.33% | 52.11% | -4.45% | 49.28% | 16.67% | 26,828.46 | 28,469.92 | 270.17 |

Interpretation:

The BTC-denominated DCI can show positive product returns in strong years such as 2020, 2023, and 2024, but the benchmark gap is often negative because simply holding BTC captures more upside. In 2020, conversion probability is 57.38%, meaning the client frequently gives up upside during a powerful rally.

Sales point:

For BTC holders, the issue is not only downside risk. The core expectation-management issue is opportunity cost. The client receives coupon income but sells part of the upside.

## Risk Management Takeaways

1. APR is not expected return.

The same 12% APR produces very different realized outcomes across years. In put-type DCI, 2023 and 2024 look acceptable, while 2022 and partial 2026 are poor.

2. Conversion probability is the first suitability metric.

For stablecoin clients, conversion means they may become BTC holders during drawdowns. For BTC clients, conversion means they may lose upside during rallies.

3. VaR and CVaR expose the tail.

The average return can look modest, but CVaR shows how bad the worst 5% of cases can be. This is the number an RM should understand before discussing yield.

4. Benchmark gap matters.

For BTC-denominated DCI, the product can have positive returns while still underperforming simple BTC holding. That is not a bug; it is the economic cost of selling upside.

5. 2026 should be read as partial.

Because the current date is 2026-06-17, the 2026 result is not a full calendar-year backtest. It is a year-to-date realized 30-day rolling test.

