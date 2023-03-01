import csv
import time
import requests
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from kucoin_futures.client import Trade
from kucoin_futures.client import User
from tradingview_ta import TA_Handler, Interval, Exchange
from datetime import datetime
from beep import beep

leverage = 10

"""
file --> btcustd 15min 60sec 4day
file2 --> btcusdt 15min 60sec 7day  with time
file3 -->btcusdt 5min 30sec 6day
file4 -->btcusdt 15min 20sec
eth   -->ethusdt 15min 30sec
"""

"""""
1 beep: open order
2 beep: error
"""""


def place_order(action):
    key = '621fefd81ca41f0001dbda27'
    secret = '4f85168b-83c2-4f5a-ad45-5db4350412b3'
    passphrase = 'Irankhahreza@9234'

    client = Trade(key=key, secret=secret, passphrase=passphrase, is_sandbox=False, )
    # client = User(key=key, secret=secret, passphrase=passphrase, is_sandbox=False, )
    err = 0
    while True:
        try:
            if action == 'short':
                order_id = client.create_market_order(symbol='XBTUSDTM', side='sell', lever=str(leverage), size='10')    # ~=20$
            elif action == 'long':
                order_id = client.create_market_order(symbol='XBTUSDTM', side='buy', lever=str(leverage), size='10')
            break
        except:
            beep(2)
            print('kucoin error')
            err += 1
            if err == 10:
                print('robot stopped due to kucoin api error')
                exit()
            time.sleep(10)
    # order_id = client.get_all_position()
    # print(order_id)


def profit_calc(order, p1, p2):
    if order == 'long':
        profit = ((p2 - p1) / p2) * 100
    else:
        profit = ((p1 - p2) / p1) * 100
    return round(profit * leverage, 2)


def timer():
    time_ = datetime.now()
    timer__ = time_.hour * 3600 + time_.minute * 60 + time_.second
    return timer__


list_csv = []
list_csv.append(
        ['RSI', 'close', 'Mom', 'SMA5', 'SMA50', 'SMA200', 'BB.upper', 'BB.lower', 'volume', 'CCI20', 'low', 'high',
         'ADX', 'ADX+DI', 'ADX-DI', 'open', 'UO', 'VWMA', 'AO', 'MACD', 'MACD.signal', 'P.SAR', 'change',
         'ATR', 'RSI7', 'ROC', 'date'])


def open_order_check():
    pos = 'close'
    order = None
    currency = TA_Handler(
        symbol="ETHUSDT",
        screener="crypto",
        exchange="KUCOIN",
        interval=Interval.INTERVAL_15_MINUTES,
    )
    currency.add_indicators(['ATR', "ROC", "RSI7"])

    while True:
        try:
            api = currency.get_analysis()
            ema = api.indicators['SMA200']
            rsi = api.indicators['RSI']
            price = api.indicators['close']
            adx = api.indicators['ADX']
            break
        except:
            beep(2)
            time.sleep(10)
    time_ = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    list_csv.append(([round(api.indicators['RSI'], 4), api.indicators['close'], api.indicators['Mom'],
                      api.indicators['SMA5'], api.indicators['SMA50'], api.indicators['SMA200'],
                      api.indicators['BB.upper'], api.indicators['BB.lower'], round(api.indicators['volume'], 4),
                      round(api.indicators['CCI20'], 3), api.indicators['low'], api.indicators['high'],
                      round(api.indicators['ADX'], 4), round(api.indicators['ADX+DI'], 4),
                      round(api.indicators['ADX-DI'], 4), api.indicators['open'], round(api.indicators['UO'], 4),
                      round(api.indicators['VWMA'], 3), round(api.indicators['AO'], 4),
                      round(api.indicators['MACD.macd'], 4), round(api.indicators['MACD.signal'], 4),
                      api.indicators['P.SAR'], round(api.indicators['change'], 4), round(api.indicators['ATR'], 4),
                      round(api.indicators['RSI7'], 4), round(api.indicators['ROC'], 4), time_]))

    f = open('file5.csv', 'w', newline='')
    writer = csv.writer(f)
    writer.writerows(list_csv)
    if adx > 25:
        if ((rsi*29) - (adx**1.5 - 50))/30 > 66:
            print('open long order at: ', price, ' | ', datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
            # place_order('long')
            pos = 'open'
            order = 'long'
            beep(1)
        elif ((rsi * 29) + (50 + adx ** 1.5)) / 30 < 34:
            print('open short order at: ', price, ' | ', datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
            # place_order('short')
            pos = 'open'
            order = 'short'
            beep(1)
    return pos, order, price


def close_order_check(order, p1):
    pos = 'open'
    currency = TA_Handler(
        symbol="ETHUSDT",
        screener="crypto",
        exchange="KUCOIN",
        interval=Interval.INTERVAL_15_MINUTES,
    )
    currency.add_indicators(['ATR', "ROC", "RSI7"])

    err = 0
    while True:
        try:
            api = currency.get_analysis()
            ema = api.indicators['SMA200']
            rsi = api.indicators['RSI']
            price = api.indicators['close']
            adx = api.indicators['ADX']
            break
        except:
            # print('tradingview error')
            beep(2)
            err += 1
            if err > 14:    #5 min
                if order == 'long':
                    print('close long order due to tradingview error')
                    # place_order('short')
                    exit()
                elif order == 'short':
                    print('close short order due to tradingview error')
                    # place_order('long')
                    exit()
            time.sleep(10)
    time_ = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    list_csv.append(([round(api.indicators['RSI'], 4), api.indicators['close'], api.indicators['Mom'],
                      api.indicators['SMA5'], api.indicators['SMA50'], api.indicators['SMA200'],
                      api.indicators['BB.upper'], api.indicators['BB.lower'], round(api.indicators['volume'], 4),
                      round(api.indicators['CCI20'], 3), api.indicators['low'], api.indicators['high'],
                      round(api.indicators['ADX'], 4), round(api.indicators['ADX+DI'], 4),
                      round(api.indicators['ADX-DI'], 4), api.indicators['open'], round(api.indicators['UO'], 4),
                      round(api.indicators['VWMA'], 3), round(api.indicators['AO'], 4),
                      round(api.indicators['MACD.macd'], 4), round(api.indicators['MACD.signal'], 4),
                      api.indicators['P.SAR'], round(api.indicators['change'], 4),round(api.indicators['ATR'], 4),
                      round(api.indicators['RSI7'], 4), round(api.indicators['ROC'], 4), time_]))
    f = open('file5.csv', 'w', newline='')
    writer = csv.writer(f)
    writer.writerows(list_csv)

    if ((rsi*29) - (adx**1.3 - 50))/30 < 60 and order == 'long':
        print('close long order at: ', price, ' | ', datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
        # place_order('short')
        print('profit:', profit_calc(order, p1=p1, p2=price), '%\n')
        pos = 'close'
        beep(1)
    elif ((rsi * 29) + (50 + adx ** 1.3)) / 30 > 40 and order == 'short':
        print('close short order at: ', price, ' | ', datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
        # place_order('long')
        print('profit:', profit_calc(order, p1=p1, p2=price), '%\n')
        pos = 'close'
        beep(1)

    return pos


timer0 = 1
while True:

    timer1 = timer()
    if abs(timer1 - timer0) < 240:    #4 min
        continue
    time.sleep(30)
    # internet_check()
    pos, order, p1 = open_order_check()
    if pos == 'open':
        while True:
            time.sleep(30)
            if close_order_check(order, p1) == 'close':
                timer0 = timer()
                break
