# Tenor Backtest: 3, 6, 9, and 12 Month BTCUSDT DCI

Execution date: 2026-06-17

Data source:

- Binance USD-M Futures daily `BTCUSDT` klines
- Entry frequency: daily rolling entries
- Tenors: 90, 180, 270, and 365 days
- Notional: 100,000 USDT
- Client APR: 12.00%

Important notes:

- 3/6/9/12 months are approximated as 90/180/270/365 days.
- This is a realized historical backtest, not a Monte Carlo simulation.
- Later years can have fewer observations for longer tenors because the terminal price must already be observable.
- 2026 has only enough data for the 90-day test as of 2026-06-17.
- Negative `VaR95 loss` means that even the 95th percentile loss threshold is still a gain versus initial notional.

## Stablecoin-Denominated DCI

Structure:

- Side: `put`
- Strike: 90% of entry spot
- Interpretation: similar to cash-secured put selling
- Main risk: BTC falls below strike and the client receives BTC after a drawdown

Command:

```powershell
python -m structuring_lab.cli dci-tenors --symbol BTCUSDT --start-year 2020 --end-year 2026 --side put --strike-moneyness 0.9 --notional 100000 --apr 0.12 --tenor-days 90 180 270 365
```

| Tenor | Year | Obs | BTC Return | Vol | DCI Return | Loss Prob | Conv Prob | VaR95 Loss | CVaR95 Loss | Bench Gap |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 90 | 2020 | 366 | 302.24% | 81.96% | 2.46% | 5.19% | 7.38% | 111.83 | 6,129.30 | 2,459.77 |
| 90 | 2021 | 365 | 57.52% | 81.14% | -7.92% | 43.56% | 45.75% | 33,629.26 | 36,603.16 | -7,922.47 |
| 90 | 2022 | 365 | -65.33% | 64.53% | -9.04% | 52.05% | 57.81% | 44,508.77 | 48,301.68 | -9,042.25 |
| 90 | 2023 | 365 | 154.75% | 43.73% | 2.84% | 2.19% | 4.66% | -2,958.90 | -2,839.57 | 2,839.57 |
| 90 | 2024 | 366 | 111.50% | 52.66% | 1.87% | 13.11% | 20.22% | 5,521.94 | 7,910.13 | 1,869.84 |
| 90 | 2025 | 365 | -7.37% | 41.76% | -2.82% | 42.19% | 46.58% | 16,269.54 | 19,879.59 | -2,818.77 |
| 90 | 2026 | 78 | -21.30% | 61.94% | -1.07% | 34.62% | 46.15% | 15,036.77 | 15,808.28 | -1,067.66 |
| 180 | 2020 | 366 | 302.24% | 81.96% | 5.92% | 0.00% | 0.00% | -5,917.81 | -5,917.81 | 5,917.81 |
| 180 | 2021 | 365 | 57.52% | 81.14% | -5.35% | 38.08% | 46.85% | 45,477.37 | 49,141.18 | -5,345.94 |
| 180 | 2022 | 365 | -65.33% | 64.53% | -14.64% | 51.51% | 54.52% | 46,528.09 | 50,617.19 | -14,641.34 |
| 180 | 2023 | 365 | 154.75% | 43.73% | 5.90% | 0.00% | 1.10% | -5,917.81 | -5,900.29 | 5,900.29 |
| 180 | 2024 | 366 | 111.50% | 52.66% | 5.56% | 1.91% | 6.28% | -4,764.42 | 781.34 | 5,563.83 |
| 180 | 2025 | 353 | -6.85% | 42.39% | -6.39% | 54.11% | 60.34% | 31,551.39 | 33,664.23 | -6,393.41 |
| 270 | 2020 | 366 | 302.24% | 81.96% | 8.88% | 0.00% | 0.00% | -8,876.71 | -8,876.71 | 8,876.71 |
| 270 | 2021 | 365 | 57.52% | 81.14% | -14.97% | 50.41% | 58.36% | 56,522.99 | 58,551.08 | -14,965.27 |
| 270 | 2022 | 365 | -65.33% | 64.53% | -11.26% | 43.01% | 44.93% | 53,796.12 | 55,521.30 | -11,264.17 |
| 270 | 2023 | 365 | 154.75% | 43.73% | 8.88% | 0.00% | 0.00% | -8,876.71 | -8,876.71 | 8,876.71 |
| 270 | 2024 | 366 | 111.50% | 52.66% | 8.88% | 0.00% | 0.00% | -8,876.71 | -8,876.71 | 8,876.71 |
| 270 | 2025 | 263 | 22.25% | 41.92% | -7.24% | 52.47% | 53.23% | 30,368.11 | 33,078.25 | -7,241.86 |
| 365 | 2020 | 366 | 302.24% | 81.96% | 12.00% | 0.00% | 0.00% | -12,000.00 | -12,000.00 | 12,000.00 |
| 365 | 2021 | 365 | 57.52% | 81.14% | -26.06% | 78.36% | 87.40% | 64,076.78 | 66,117.47 | -26,064.23 |
| 365 | 2022 | 365 | -65.33% | 64.53% | -1.04% | 34.52% | 39.73% | 38,635.56 | 46,947.48 | -1,037.37 |
| 365 | 2023 | 365 | 154.75% | 43.73% | 12.00% | 0.00% | 0.00% | -12,000.00 | -12,000.00 | 12,000.00 |
| 365 | 2024 | 366 | 111.50% | 52.66% | 11.84% | 0.00% | 3.83% | -12,000.00 | -11,840.55 | 11,840.55 |
| 365 | 2025 | 168 | 10.50% | 47.96% | -2.15% | 49.40% | 86.31% | 24,341.34 | 26,796.36 | -2,149.45 |

Put-side interpretation:

- Longer tenors increase the visible coupon, but they also keep the client exposed to a longer BTC drawdown window.
- 2021 and 2022 are the warning years. A 12-month put-side DCI entered during 2021 had an 87.40% conversion rate and a -26.06% average realized product return.
- 2023 and 2024 look favorable across longer tenors because BTC did not frequently finish below 90% of entry spot at maturity.
- 2025 becomes problematic for longer tenors despite the displayed coupon because completed observations include many entries that later experienced downside conversion.

## BTC-Denominated DCI

Structure:

- Side: `call`
- Strike: 110% of entry spot
- Interpretation: similar to covered call selling
- Main risk: BTC rallies above strike and the client gives up upside

Command:

```powershell
python -m structuring_lab.cli dci-tenors --symbol BTCUSDT --start-year 2020 --end-year 2026 --side call --strike-moneyness 1.1 --notional 100000 --apr 0.12 --tenor-days 90 180 270 365
```

| Tenor | Year | Obs | BTC Return | Vol | DCI Return | Loss Prob | Conv Prob | VaR95 Loss | CVaR95 Loss | Bench Gap |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 90 | 2020 | 366 | 302.24% | 81.96% | 9.88% | 13.93% | 80.05% | 10,100.65 | 15,516.37 | -55,223.10 |
| 90 | 2021 | 365 | 57.52% | 81.14% | -7.00% | 49.04% | 43.01% | 40,266.34 | 42,942.84 | -12,243.90 |
| 90 | 2022 | 365 | -65.33% | 64.53% | -12.16% | 68.49% | 20.27% | 50,057.89 | 53,471.52 | -2,780.02 |
| 90 | 2023 | 365 | 154.75% | 43.73% | 9.29% | 12.88% | 63.29% | 7,220.91 | 9,390.06 | -16,133.56 |
| 90 | 2024 | 366 | 111.50% | 52.66% | 4.80% | 29.51% | 45.90% | 14,969.75 | 17,119.12 | -13,848.91 |
| 90 | 2025 | 365 | -7.37% | 41.76% | -3.97% | 56.16% | 28.77% | 24,642.59 | 27,891.63 | -990.46 |
| 90 | 2026 | 78 | -21.30% | 61.94% | -2.84% | 58.97% | 32.05% | 23,533.10 | 24,227.45 | 1,039.65 |
| 180 | 2020 | 366 | 302.24% | 81.96% | 16.36% | 0.00% | 96.99% | -16,509.59 | -15,563.57 | -146,563.39 |
| 180 | 2021 | 365 | 57.52% | 81.14% | -6.68% | 53.70% | 27.12% | 50,929.64 | 54,227.06 | -1,566.93 |
| 180 | 2022 | 365 | -65.33% | 64.53% | -14.87% | 58.08% | 35.62% | 51,875.28 | 55,555.47 | -8,496.52 |
| 180 | 2023 | 365 | 154.75% | 43.73% | 14.84% | 3.56% | 86.30% | -1,563.52 | 1,857.00 | -43,203.71 |
| 180 | 2024 | 366 | 111.50% | 52.66% | 13.21% | 9.84% | 75.14% | 5,712.02 | 10,703.20 | -16,311.62 |
| 180 | 2025 | 353 | -6.85% | 42.39% | -7.86% | 61.19% | 34.84% | 38,396.25 | 40,297.80 | -267.44 |
| 270 | 2020 | 366 | 302.24% | 81.96% | 19.76% | 0.00% | 100.00% | -19,764.38 | -19,764.38 | -235,544.26 |
| 270 | 2021 | 365 | 57.52% | 81.14% | -15.58% | 59.18% | 29.59% | 60,870.69 | 62,695.97 | -1,824.15 |
| 270 | 2022 | 365 | -65.33% | 64.53% | -8.24% | 44.93% | 54.52% | 58,416.51 | 59,969.17 | -10,745.24 |
| 270 | 2023 | 365 | 154.75% | 43.73% | 19.76% | 0.00% | 100.00% | -19,764.38 | -19,764.38 | -68,389.40 |
| 270 | 2024 | 366 | 111.50% | 52.66% | 19.76% | 0.00% | 98.36% | -19,764.38 | -19,737.09 | -30,259.97 |
| 270 | 2025 | 263 | 22.25% | 41.92% | -8.90% | 53.99% | 14.07% | 37,331.30 | 39,770.49 | 6,463.09 |
| 365 | 2020 | 366 | 302.24% | 81.96% | 23.20% | 0.00% | 100.00% | -23,200.00 | -23,200.00 | -349,953.30 |
| 365 | 2021 | 365 | 57.52% | 81.14% | -31.17% | 87.12% | 7.67% | 67,669.10 | 69,505.73 | 6,534.24 |
| 365 | 2022 | 365 | -65.33% | 64.53% | 1.60% | 38.63% | 55.34% | 44,772.00 | 52,252.73 | -19,992.36 |
| 365 | 2023 | 365 | 154.75% | 43.73% | 23.20% | 0.00% | 100.00% | -23,200.00 | -23,200.00 | -105,981.74 |
| 365 | 2024 | 366 | 111.50% | 52.66% | 20.62% | 3.28% | 86.61% | -1,479.26 | 1,874.33 | -41,689.69 |
| 365 | 2025 | 168 | 10.50% | 47.96% | -11.28% | 83.93% | 0.00% | 31,907.20 | 34,116.72 | 9,505.18 |

Call-side interpretation:

- Longer-tenor call-side DCI can produce high product returns when BTC rallies and conversion happens, because the client is converted at 110% of entry spot plus coupon.
- That same conversion is a major opportunity cost against simple BTC holding. In 2020, the 12-month call-side DCI shows a 23.20% product return, but an average benchmark gap of -349,953.30 versus holding BTC.
- In strong BTC years, the client may feel they "made money" while still materially underperforming BTC.
- In weak years, call-side DCI can still lose money because the client starts with BTC exposure and the coupon is not enough to offset BTC drawdowns.

## Risk Management Takeaways

1. Longer tenor is not automatically safer.

A longer holding period increases coupon accrual, but it also increases the window over which BTC can cross the strike and produce conversion or opportunity cost.

2. Put-side and call-side suitability are different.

Stablecoin clients care about downside conversion into BTC. BTC clients care about upside being capped or sold away.

3. Benchmark gap becomes more important as tenor increases.

For BTC-denominated DCI, 9- and 12-month structures can look attractive on product return while badly lagging BTC in bull markets.

4. Partial-year observations must be treated carefully.

Long-tenor tests require future terminal prices. As of 2026-06-17, 2026 cannot yet be evaluated for 180/270/365-day tenors, and 2025 has fewer observations for longer tenors.

5. Sales language should change by tenor.

For 3-month products, the conversation can focus on near-term strike risk. For 12-month products, the conversation must include regime risk, benchmark opportunity cost, and the possibility that a superficially high coupon is small relative to BTC movement.

