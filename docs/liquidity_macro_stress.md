# Liquidity and Macro-Rate Stress Test

Execution date: 2026-06-17

Data sources:

- Binance USD-M Futures daily `BTCUSDT` klines
- FRED `DGS3MO`: 3-Month Treasury Constant Maturity Rate
- FRED `FEDFUNDS`: Effective Federal Funds Rate

Command:

```powershell
python -m structuring_lab.cli stress --symbol BTCUSDT --start-year 2020 --end-year 2026 --window 30 --stress-percentile 90
```

## Why Rates Matter

Lending rates, policy rates, and short-term Treasury yields affect crypto structured products through several channels.

1. Hurdle rate

If 3-month Treasury bills yield 5%, a 12% APR crypto structured product is not competing against zero. The incremental spread is compensation for option risk, liquidity risk, counterparty risk, custody risk, stablecoin risk, and operational risk.

2. Funding and hedge cost

Structured products are hedged with spot, perpetuals, futures, options, or OTC liquidity. Higher fiat rates and higher crypto lending rates can increase funding costs and make hedging more expensive.

3. Opportunity cost

Stablecoin holders can compare a crypto yield product against Treasury bills, money-market funds, repo-like products, or secured lending. BTC holders compare yield products against BTC upside.

4. Liquidity and redemption risk

In market stress, lending rates can spike, liquidity can disappear, collateral haircuts can increase, and early redemption can become costly or impossible. This matters for Stable-Return products and basis/funding strategies.

## Liquidity Stress Proxy

Binance daily klines do not contain order book depth or bid-ask spreads. Therefore this project uses a proxy stress score based on:

- Intraday range: `(high - low) / close`
- 30-day realized volatility
- 30-day rolling max drawdown
- Amihud-style illiquidity: `abs(return) / quote_volume_in_millions`

Liquidity-constrained days are defined as the top 10% stress-score days over the full sample.

This is not a full market microstructure liquidity model. It is a practical first approximation for identifying periods when pricing, hedging, and exits are likely to be more difficult.

## Yearly Stress Summary

| Year | Obs | BTC Return | MDD | Stress Days | Stress Ratio | Stress MDD | Vol | Range | Illiq | 3M Bill | FedFunds | Max 3M |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 2020 | 366 | 302.24% | -54.00% | 67 | 18.31% | -53.17% | 69.70% | 5.18% | 0.000009 | 0.37% | 0.37% | 1.59% |
| 2021 | 365 | 57.52% | -53.22% | 101 | 27.67% | -48.47% | 78.88% | 7.04% | 0.000002 | 0.05% | 0.08% | 0.09% |
| 2022 | 365 | -65.33% | -66.94% | 54 | 14.79% | -63.14% | 63.19% | 4.90% | 0.000002 | 2.08% | 1.69% | 4.46% |
| 2023 | 365 | 154.75% | -20.01% | 0 | 0.00% | n/a | 41.75% | 3.45% | 0.000001 | 5.27% | 5.03% | 5.63% |
| 2024 | 366 | 111.50% | -26.26% | 2 | 0.55% | 0.00% | 51.13% | 4.23% | 0.000001 | 5.18% | 5.14% | 5.52% |
| 2025 | 365 | -7.37% | -32.05% | 0 | 0.00% | n/a | 40.94% | 3.42% | 0.000001 | 4.21% | 4.21% | 4.46% |
| 2026 | 168 | -26.82% | -37.21% | 10 | 5.95% | -8.39% | 45.40% | 3.71% | 0.000001 | 3.70% | 3.64% | 3.80% |

## Interpretation

### 2020 and 2021: low rates did not mean low crypto stress

Policy rates and Treasury yields were near zero, but BTC still had large drawdowns and many liquidity-stress days. This shows that crypto liquidity stress can be driven by leverage, positioning, volatility, and market structure, not just macro rates.

### 2022: drawdown and rate shock overlapped

2022 is the clearest stress year in this sample. BTC fell sharply, max drawdown reached -66.94%, and 3-month Treasury yields rose from near zero to above 4% by year-end. For a structured product seller, this is a dangerous combination:

- underlying drawdown risk increases;
- funding and hedging conditions worsen;
- clients can compare crypto yield against higher Treasury yields;
- liquidity and redemption pressure can rise.

### 2023 and 2024: high rates raised the hurdle, but BTC stress was lower

Average 3-month Treasury yields were above 5%, but BTC performed strongly and liquidity-stress days were low in this proxy. This does not mean rates are irrelevant. It means rates are not a complete stress predictor. Their main effect here is on product economics: a 12% APR product must justify its spread over a 5% risk-free-like alternative.

### 2026: partial year

2026 is only year-to-date through 2026-06-17. The sample shows negative BTC return, a -37.21% max drawdown, and a 5.95% liquidity-stress-day ratio.

## Product Design Implications

For DCI:

- Higher Treasury yields make the required coupon higher.
- A low coupon spread over T-bills is harder to justify if the client is selling option risk.
- In stress regimes, conversion probability and tail loss should be shown alongside the yield quote.

For Stable-Return or lending-based products:

- The return engine should be separated into Treasury yield, lending spread, funding/basis, and option premium.
- Lending rate is not a free yield. It embeds borrower credit risk, collateral liquidation risk, platform risk, and liquidity lockup risk.
- If liquidity is restricted, realized maximum drawdown and early-exit cost can dominate the stated APR.

## Suggested Risk Features

For future product scoring, use these features before approving a quote:

- 30-day realized volatility
- 30-day rolling max drawdown
- intraday range percentile
- Amihud-style illiquidity
- funding rate level and sign
- 3-month Treasury yield
- effective Fed funds rate
- lending rate spread over Treasury bills
- stablecoin depeg stress indicator
- exchange/order-book depth if available

## Sales Framing

A client-facing explanation should say:

> The quoted APR should be compared with short-term Treasury yields and lending rates. The spread is compensation for structured-product risks, including option exposure, conversion risk, liquidity restrictions, counterparty risk, and drawdown risk. In stressed liquidity regimes, historical maximum drawdown and exit constraints can matter more than the headline yield.

