import unittest

from structuring_lab.products import DualCurrencyInvestment
from structuring_lab.risk import summarize_values


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


if __name__ == "__main__":
    unittest.main()

