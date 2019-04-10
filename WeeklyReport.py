from Robinhood import Robinhood
from ScannerClasses import TimeManager
from ScannerClasses import Trader
import random
import smtplib
import getpass
import config

# initiate objects used for logic
message = "Stocks to buy: \n\n Ticker | Ratio \n __________________\n"
time_manager = TimeManager()
stocks_to_buy = {}
company_list = []
company_file = open('company_symbols.txt')
for line in company_file:
    company_list.append(line.strip('\n'))
random.shuffle(company_list)
trader = Trader()
ctr = len(company_list)
# cycle through all stocks to pick potential buys
for ticker in company_list:
    trader = Trader()
    if ticker != None:
        try:
            print(ctr)
            ctr -= 1
            stock_price = trader.my_trader.get_quote(ticker)
            stock_info = trader.my_trader.fundamentals(ticker)
            current_price = float(stock_price['last_extended_hours_trade_price'])
            year_low = float(stock_info['low_52_weeks'])
            ratio_to_low = (current_price - year_low) / year_low
            if ratio_to_low <= 0.01:
                stocks_to_buy[ticker] = ratio_to_low
        except Exception as e:
            print(e)
            continue
# log and send list of stock recomendations
with open(time_manager.log_file_name, 'a') as log_file:
    port = 587
    smtp_server = "smtp.gmail.com"
    receiver_email = config.config["receiver"]
    sender_email =  config.config["username"]
    password = config.config["password"]
    for ticker, ratio in stocks_to_buy.items():
        message += str(ticker) + " : " + str(ratio) + "\n"
    try:
        server = smtplib.SMTP(
            smtp_server, port)
        server.starttls()
        server.login(sender_email, password)
        log_file.write(message)
        server.sendmail(
            sender_email, receiver_email, message)
    except Exception as error: 
        print('ERROR', error) 
