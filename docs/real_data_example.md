# Real Data Example: BTCUSDT DCI and Funding

Execution date: 2026-06-17

Data source:

- Binance USD-M Futures `BTCUSDT` kline data
- Binance USD-M Futures `BTCUSDT` funding rate history

This note shows how to use the project with live public market data. The numbers below are examples from one execution and will change as Binance market data updates.

## 1. Stablecoin-Denominated DCI

Command:

```powershell
python -m structuring_lab.cli dci --symbol BTCUSDT --lookback 365 --side put --strike-moneyness 0.9 --notional 100000 --apr 0.12 --tenor-days 30 --paths 20000 --seed 42
```

Inputs and market estimates:

- Spot: 64,684.80
- Strike: 58,216.32
- Notional: 100,000 USDT
- Tenor: 30 days
- Client APR: 12.00%
- Historical annualized volatility: 43.13%
- Simulation drift: 0.00%

Risk summary:

- Expected value: 99,530.87
- Expected return: -0.47%
- Probability of loss: 19.35%
- Conversion probability: 21.62%
- VaR 95 loss: 9,339.79
- CVaR 95 loss: 13,639.49
- Worst / best value: 68,434.35 / 100,986.30
- Expected benchmark gap: -469.13

Option reference:

- Black-Scholes put premium on product quantity: 1,426.21
- BS-implied fair APR before margin/share split: 17.35%

Interpretation:

The customer sees a 12.00% APR quote, but the simulation estimates a negative expected return after accounting for conversion risk. The Black-Scholes reference suggests that the embedded put option risk is worth around 17.35% APR before any platform margin or revenue split. In this run, 12.00% APR does not appear rich enough to compensate for the downside conversion risk.

## 2. BTC-Denominated DCI

Command:

```powershell
python -m structuring_lab.cli dci --symbol BTCUSDT --lookback 365 --side call --strike-moneyness 1.1 --notional 100000 --apr 0.12 --tenor-days 30 --paths 20000 --seed 42
```

Inputs and market estimates:

- Spot: 64,652.10
- Strike: 71,117.31
- Notional value: 100,000 USDT equivalent in BTC
- Tenor: 30 days
- Client APR: 12.00%
- Historical annualized volatility: 43.13%
- Simulation drift: 0.00%

Risk summary:

- Expected value: 99,302.96
- Expected return: -0.70%
- Probability of loss: 49.36%
- Conversion probability: 20.46%
- VaR 95 loss: 18,406.48
- CVaR 95 loss: 22,276.32
- Worst / best value: 61,589.76 / 111,084.93
- Expected benchmark gap: -647.89

Option reference:

- Black-Scholes call premium on product quantity: 1,638.91
- BS-implied fair APR before margin/share split: 19.94%

Interpretation:

This structure is similar to covered call selling. The customer earns coupon-like income, but gives up upside beyond the strike. Compared with simply holding BTC, the expected benchmark gap is negative in this run. That is the sales explanation point: the product is not just a yield product. It is a yield-versus-upside tradeoff.

## 3. Funding Rate Summary

Command:

```powershell
python -m structuring_lab.cli funding --symbol BTCUSDT --limit 1000
```

Observed sample:

- First funding time: 2026-04-12T00:00:00+00:00
- Last funding time: 2026-06-17T08:00:00+00:00
- Observations: 200

Funding summary:

- Mean funding rate per event: 0.0005%
- Median funding rate per event: 0.0004%
- Std funding rate per event: 0.0049%
- Positive funding probability: 55.00%
- Annualized mean funding: 0.52%
- Cumulative simple funding over sample: 0.10%
- Worst / best event: -0.0123% / 0.0100%

Interpretation:

In this sample, BTCUSDT funding is positive slightly more often than negative, but the annualized average is only about 0.52%. That is far below the 12% APR used in the DCI examples. Therefore, if a product advertises a much higher stable return, the return engine is unlikely to be funding alone. It probably needs additional sources such as option premium, basis trades, lending, leverage, or inventory/risk warehousing.

## Sales and Risk Management Takeaway

For client communication, the central message is:

> The displayed APR is not the expected return. The product embeds option-like risk, conversion risk, and tail loss. We should explain the probability of conversion, expected value, VaR/CVaR, and the benchmark gap before discussing yield.

This is the practical distinction between selling a yield number and explaining a structured derivative.

