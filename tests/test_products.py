import unittest
from datetime import datetime, timedelta, timezone

from structuring_lab.backtest import rolling_dci_backtest_by_year
from structuring_lab.binance import Kline
from structuring_lab.products import DualCurrencyInvestment
from structuring_lab.risk import summarize_funding_rates, summarize_values
from structuring_lab.stress import StressDay, detect_liquidity_drawdown_events, max_drawdown


class DualCurrencyInvestmentTests(unittest.TestCase):
    def test_put_side_converts_below_strike(self):
        product = DualCurrencyInvestment(
            spot=100000,
            strike=90000,
            notional_quote=100000,
            apr=0.12,
            tenor_days=30,
            side="put",
        )

        result = product.evaluate(81000)

        self.assertTrue(result.converted)
        self.assertLess(result.settlement_value_quote, 100000)

    def test_put_side_keeps_quote_above_strike(self):
        product = DualCurrencyInvestment(
            spot=100000,
            strike=90000,
            notional_quote=100000,
            apr=0.12,
            tenor_days=30,
            side="put",
        )

        result = product.evaluate(95000)

        self.assertFalse(result.converted)
        self.assertGreater(result.settlement_value_quote, 100000)

    def test_call_side_underperforms_hodl_above_strike(self):
        product = DualCurrencyInvestment(
            spot=100000,
            strike=110000,
            notional_quote=100000,
            apr=0.12,
            tenor_days=30,
            side="call",
        )

        result = product.evaluate(130000)

        self.assertTrue(result.converted)
        self.assertLess(result.settlement_value_quote, result.benchmark_value_quote)

    def test_risk_summary_reports_loss_probability(self):
        summary = summarize_values([90, 100, 110], initial_value=100)

        self.assertAlmostEqual(summary.probability_of_loss, 1 / 3)
        self.assertAlmostEqual(summary.expected_value, 100)

    def test_funding_summary_annualizes_event_rates(self):
        summary = summarize_funding_rates([0.0001, -0.00005, 0.0002], events_per_day=3)

        self.assertEqual(summary.observations, 3)
        self.assertAlmostEqual(summary.positive_probability, 2 / 3)
        self.assertAlmostEqual(summary.annualized_mean_rate, 0.00025 / 3 * 3 * 365)

    def test_yearly_backtest_groups_by_entry_year(self):
        start = datetime(2020, 1, 1, tzinfo=timezone.utc)
        rows = [
            Kline(
                open_time=start + timedelta(days=index),
                open=100 + index,
                high=100 + index,
                low=100 + index,
                close=100 + index,
                volume=1,
                close_time=start + timedelta(days=index, hours=23, minutes=59),
                quote_volume=1,
                trades=1,
            )
            for index in range(40)
        ]

        results = rolling_dci_backtest_by_year(
            rows,
            start_year=2020,
            end_year=2020,
            side="put",
            strike_moneyness=0.9,
            notional=100000,
            apr=0.12,
            tenor_days=30,
        )

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].year, 2020)
        self.assertEqual(results[0].observations, 10)

    def test_max_drawdown(self):
        self.assertAlmostEqual(max_drawdown([100, 120, 90, 96]), -0.25)

    def test_detect_liquidity_drawdown_events(self):
        start = datetime(2020, 1, 1, tzinfo=timezone.utc)
        days = []
        for index, close in enumerate([100, 95, 90, 91]):
            day = start + timedelta(days=index)
            days.append(
                StressDay(
                    date=day.date(),
                    close=close,
                    quote_volume=1,
                    daily_return=0,
                    range_pct=0.1,
                    rolling_volatility=0.5,
                    rolling_drawdown=-0.1,
                    amihud_illiq=0.1,
                    t_bill_3m=0.01,
                    fed_funds=0.01,
                    stress_score=2.0,
                    liquidity_constrained=index in {1, 2},
                )
            )

        events = detect_liquidity_drawdown_events(days, min_drawdown=-0.05)

        self.assertEqual(len(events), 1)
        self.assertEqual(events[0].stress_days, 2)
        self.assertAlmostEqual(events[0].max_drawdown, -0.052631578947368474)


if __name__ == "__main__":
    unittest.main()
