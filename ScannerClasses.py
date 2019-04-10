import datetime
import time
from Robinhood import Robinhood
from alpha_vantage.timeseries import TimeSeries
import getpass
import config

class TimeManager:
    log_time = str(datetime.datetime.now())
    log_file_name = "logs/log_" + log_time + ".txt"
    current_hour = datetime.datetime.now().hour
    current_min = datetime.datetime.now().minute
    run_time_limit = 10
    program_limit = 60
    market_start_hour = 10
    market_end_hour = 16

    def time(self, stock):
        self.now_hour = datetime.datetime.now().time().hour
        self.now_min = datetime.datetime.now().time().minute
        self.now_sec = datetime.datetime.now().time().second
        self.hour_diff = ((int(stock.updated_at[0])) - 5) - self.now_hour
        self.min_diff = int(stock.updated_at[1]) - self.now_min
        self.sec_diff = int(stock.updated_at[2]) - self.now_sec

    def run_start(self):
        self.run_start_time = time.time()

    def start(self):
        self.start_time = time.time()
    
    def run_time(self):
        self.end_time = time.time()
        self.run_time_diff = self.end_time - self.run_start_time

    def program_time(self):
        self.end_time = time.time()
        self.program_time_diff = self.end_time - self.start

    def reset(self):
        self.current_hour = datetime.datetime.now().hour
        self.current_min = datetime.datetime.now().minute
        self.end_time = time.time()
        self.time_diff = self.end_time - self.start_time

class MoneyManager: 
    def __init__(self):
        self.portfolio = 1000
        self.budget = 2000
        self.layover_investment = 0.0
        self.total_profit = 0.0
        self.max_buy = 100
        self.min_buy = 10
        self.program_limit = 60
        self.run_time = 10
        self.open_price = 0.0
        self.run_investment = 0.0
        self.new_price = 0.0
        self.run_profit = 0.0
        self.diff = 0.0
        self.cur_stock = Stock()
        self.new_stock = Stock()
        self.stocks = {}
        self.original_stocks = {}  
        self.companies = []  

    def current_stock(self, trader, item):
        self.stock = trader.my_trader.quote_data(item)
        self.updated = self.stock['updated_at']
        self.updated = self.updated.split("T",1)[1]
        self.updated = self.updated.split("Z",1)[0]
        self.updated = self.updated.split(":")

    def determine_invest(self, timeManager, stock):
        ask_price = float(stock.ask_price)
        if ask_price >= self.min_buy and ask_price < self.max_buy:
            if self.run_investment + ask_price < self.budget: 
                ts = TimeSeries(key='2Y13432WDGD7R7OV')
                meta_data = ts.get_daily('AAPL', outputsize='full')[0]
                yesterday = datetime.datetime.strftime(datetime.datetime.now() - datetime.timedelta(1), '%Y-%m-%d')
                if meta_data[yesterday]['5. volume'] >= 500000:
                    # invest
                    if self.stocks.get(stock.symbol) == None:
                        self.stocks[stock.symbol] = stock
                        self.original_stocks[stock.symbol] = stock
                        self.run_investment += float(stock.ask_price)

    def determine_sell(self):
        self.diff = self.new_stock.ask_price - self.cur_stock.ask_price
        if self.diff < 0.0:
            # sell and adjust numbers
            self.run_profit += (self.new_stock.ask_price - self.original_stocks[self.cur_stock.symbol].ask_price)
            del self.stocks[self.cur_stock.symbol]
            del self.original_stocks[self.cur_stock.symbol]
        else:
            self.stocks[self.cur_stock.symbol] = self.new_stock

    def determine_sell_all(self, timeManager, ticker):
        if timeManager.time_diff > timeManager.program_limit:
            self.run_profit += (self.new_stock.ask_price - self.original_stocks[ticker].ask_price)
            del self.stocks[ticker]
            del self.original_stocks[ticker]
            return True
        else:
            return False

    def crunch_numbers(self):
        self.total_profit += self.run_profit
        self.budget += self.run_profit
        self.portfolio += self.run_profit
        self.layover_investment = 0
        for key in self.stocks.keys(): 
            self.layover_investment += self.original_stocks[key].ask_price
        self.budget = self.portfolio - self.layover_investment
        self.run_investment = 0.0
        self. open_price = 0.0

class Stock: 
    def __init__(self, trader=None, ticker=None):
        if trader != None:
            trader_stock = trader.my_trader.quote_data(ticker)
            self.adjusted_previous_close = trader_stock["adjusted_previous_close"]
            self.ask_price = trader_stock["ask_price"]
            self.ask_size = trader_stock["ask_size"]
            self.bid_price = trader_stock["bid_price"]
            self.bid_size = trader_stock["bid_size"]
            self.has_traded = trader_stock["has_traded"]
            self.instrument = trader_stock["instrument"]
            self.last_exteneded_hours_trade_price = trader_stock["last_extended_hours_trade_price"]
            self.last_trade_price = trader_stock["last_trade_price"]
            self.last_trade_price_source = trader_stock["last_trade_price_source"]
            self.previous_close = trader_stock["previous_close"]
            self.previous_close_date = trader_stock["previous_close_date"]
            self.symbol = trader_stock["symbol"]
            self.trading_halted = trader_stock["trading_halted"]
            self.updated_at = trader_stock["updated_at"]
            self.updated_at = self.updated_at.split("T",1)[1]
            self.updated_at = self.updated_at.split("Z",1)[0]
            self.updated_at = self.updated_at.split(":")
        else:
            self.adjusted_previous_close = ""
            self.ask_price = ""
            self.ask_size = ""
            self.bid_price = ""
            self.bid_size = ""
            self.has_traded = ""
            self.instrument = ""
            self.last_exteneded_hours_trade_price = ""
            self.last_trade_price = ""
            self.last_trade_price_source = ""
            self.previous_close = ""
            self.previous_close_date = ""
            self.symbol = ""
            self.trading_halted = ""
            self.updated_at = ""

class Trader:
    my_trader = Robinhood()
    username = config.config["username"]
    password = config.config["password"]
    logged_in = my_trader.login(username=username, password=password)
