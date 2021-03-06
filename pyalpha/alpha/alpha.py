import datetime
import pickle
import os
from abc import ABCMeta, abstractmethod

import ystockquote
import numpy as np

from pyalpha.data_structures.historical_stock import HistoricalStock


class Alpha(metaclass=ABCMeta):
    """
    Abstract class to compute alphas

    **Methods**::

    - construct_historical_data(self)
    - verify_historical_data(self)
    - save_data(self, file_name)
    - load_data(self, file_name)
    - alpha(self, stock)
    - simulate(self)

    """
    def __init__(self, stock_list, start_date, end_date):

        self.start_date = start_date
        self.end_date = end_date
        self.stock_list = stock_list
        self.data = {}

        self.funds = 1000000
        self.turnover = [0]
        self.returns = []

    def construct_historical_data(self):
        """
        - Creates a data structure of historical stock data
        - The data structure is a dictionary which maps the dates to
          a list of HistoricalStock instances, which contain the stock's
          data on the given date for each stock in the stock list.

        Stock lists are user defined.
        Stock lists for SNP100 and SNP500 available in *stock_lists.py*.
        """
        for stock in self.stock_list:
            response = ystockquote.get_historical_prices(stock,
                                                         self.start_date,
                                                         self.end_date)
            print(stock)
            for date_str, value in response.items():
                h = HistoricalStock(stock, date_str)
                h.set_data(value)
                d = date_str.split("-")
                date = datetime.date(int(d[0]), int(d[1]), int(d[2]))
                if date not in self.data.keys():
                    self.data[date] = []
                self.data[date].append(h)
        self.verify_historical_data()

    def verify_historical_data(self):
        stock_count = []
        for key in self.data.keys():
            stock_count.append(len(self.data[key]))
        max_len = max(stock_count)
        to_delete = []
        for key in self.data.keys():
            if len(self.data[key]) < max_len:
                to_delete.append(key)
        for key in to_delete:
            self.data.pop(key)

    def save_data(self, file_name='stock_data.pickle'):
        """
        - Saves the stock data to a pickle file locally
        """
        if os.path.isfile(file_name):
            print("A stock_data file with the same name already exists")
            return
        with open(file_name, 'wb') as data_file:
            pickle.dump(self.data, data_file, -1)

    def load_data(self, file_name='stock_data.pickle'):
        """
        - Loads the stock_data from a pickle file
        """
        try:
            with open(file_name, 'rb') as data_file:
                self.data = pickle.load(data_file)
        except FileNotFoundError:
            print("Specified stock_data file does not exist")
            return

    @abstractmethod
    def alpha(self, stock):
        """
        :Abstract Method: Needs to be defined by the user

        - Sets the weight for each stock
        - All parameters available in HistoricalStock can be used in here
        - Returns a single decimal giving the weight of a stock

        """
        pass

    def simulate(self):
        """
        - Runs the simulation for the user-defined alpha
        - Calculates the cumulative return, turnover
        """
        self.turnover = [0]
        self.returns = []
        stock_vector_old = None
        days = []
        for key in self.data.keys():
            days.append(key)

        days = sorted(days)
        for i in range(1, len(days)):
            data_day = days[i-1]
            trading_day = days[i]

            alpha_stock = []
            stock_prices_open = []
            stock_prices_close = []

            # Use the information obtained on the previous day to make
            # trades on the present day. Stocks are purchased when the
            # exchange opens and are sold as it closes.

            for stock in self.data[data_day]:
                alpha_stock.append(self.alpha(stock))
            for stock in self.data[trading_day]:
                stock_prices_open.append(stock.open)
                stock_prices_close.append(stock.close)

            alpha_total = sum(alpha_stock)
            stock_vector = []
            returns_day = 0

            for j in range(len(alpha_stock)):
                quantity = int(alpha_stock[j] * self.funds
                               / (alpha_total * stock_prices_open[j]))
                stock_vector.append(quantity)
                return_on_stock = ((stock_prices_close[j] -
                                    stock_prices_open[j]) * quantity)
                self.data[trading_day][j].returns = return_on_stock
                returns_day += return_on_stock

            self.returns.append(returns_day * 100.0 / self.funds)
            self.funds += returns_day

            if stock_vector_old is not None:
                turnover_day = np.dot(stock_vector, stock_vector_old)
                self.turnover.append(turnover_day)
            stock_vector_old = stock_vector
