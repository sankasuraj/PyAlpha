import unittest

from pyalpha.data_structures.historical_stock import HistoricalStock
from pyalpha.data_structures.stock import Stock
from pyalpha.portfolio.portfolio import Portfolio


class TestPortfolio(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pf = Portfolio()
        cls.rich = cls.pf.add_person("Rich", 1000000)
        cls.poor = cls.pf.add_person("Poor", 10)

    def test_stock_price_fetch(self):
        tesla = Stock()
        tesla.fetch_price()
        self.assertTrue(tesla.price > 0)

    def test_historical_price_fetch(self):
        tesla_historical = HistoricalStock()
        tesla_historical.fetch_prices()
        self.assertTrue(tesla_historical.high >= tesla_historical.low)
        self.assertTrue(tesla_historical.low > 0)

    def test_get_stock_quote(self):
        value = TestPortfolio.rich._get_stock_quote("TSLA")
        self.assertTrue(value > 0)

    def test_buy_stock_sufficient_balance(self):
        self.assertTrue(TestPortfolio.rich.buy_stock("AAPL", 2))
        self.assertTrue(TestPortfolio.rich.buy_stock("AAPL", 2))

    def test_buy_stock_insufficient_balance(self):
        self.assertFalse(TestPortfolio.poor.buy_stock("AAPL", 20))

    def test_sell_stock_sufficient_stocks_available(self):
        self.assertTrue(TestPortfolio.rich.sell_stock("AAPL", 1))

    def test_sell_stock_insufficient_stocks_available(self):
        self.assertFalse(TestPortfolio.rich.sell_stock("AAPL", 20))

    def test_funds_deposit(self):
        deposit = 1000
        balance = TestPortfolio.rich.balance
        TestPortfolio.rich.add_funds(deposit)
        self.assertEqual(balance + deposit, TestPortfolio.rich.balance)

    def test_funds_withdrawal(self):
        withdrawal = 1000
        balance = TestPortfolio.rich.balance
        TestPortfolio.rich.add_funds(-1 * withdrawal)
        # Should not withdraw funds
        self.assertEqual(balance, TestPortfolio.rich.balance)

    def test_check_logs(self):
        self.assertTrue(len(TestPortfolio.rich.view_portfolio().axes[0]))

    def tearDown(self):
        pass


if __name__ == '__main__':
    unittest.main()
