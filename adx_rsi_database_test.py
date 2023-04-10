import time
import requests
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from kucoin_futures.client import Trade
from kucoin_futures.client import User
from tradingview_ta import TA_Handler, Interval, Exchange
from datetime import datetime
from beep import beep
import csv

leverage = 10
index = 0    #The index that under consideration
while True:
    input_ = input('1.file1\n2.file2\n3.file3\n4.file4\ne.eth\n5.file5\n')
    if input_ == '1':
        time_row = None; file = 'file.csv'
    elif input_ == '2':
        time_row = 16; file = 'file2.csv'
    elif input_ == '3':
        time_row = 20; file = 'file3.csv'
    elif input_ == '4':
        time_row = 20; file = 'file4.csv'
    elif input_ == 'e':
        time_row = 20; file = 'eth.csv'
    elif input_ == '5':
        time_row = 26; file = 'file5.csv'
    else:
        print('wrong input'); exit()
    break
"""
file --> btcustd 15min 60sec 4day
file2 --> btcusdt 15min 60sec 7day  with time
file3 -->btcusdt 5min 30sec 6day
file4 -->btcusdt 15min 20sec
eth   -->ethusdt 15min 30sec
"""
"""""
1 beep: open order
2 beep: internet error & tradingwiev api error
3 beep: error
"""""
order_counter = 0

file = open(file)
csvreader = csv.reader(file)
rows = []
for row in csvreader:
        rows.append(row)
print('records:', len(rows), '\n')
del rows[0]


list_profit = []
def profit_calc(order, p1, p2, leverage=leverage):
    if order == 'long':
        profit = ((p2 - p1) / p2) * 100
    else:
        profit = ((p1 - p2) / p1) * 100
    list_profit.append(profit * leverage)
    return round(profit * leverage, 2)

def profit_calc_(order, p1, p2, leverage=leverage):
    if order == 'long':
        profit = ((p2 - p1) / p2) * 100
    else:
        profit = ((p1 - p2) / p1) * 100
        ##################3
    return round(profit * leverage, 2)

def timer():
    if time_row is None:
        return 241
    h = int(rows[index][time_row][11] + rows[index][time_row][12])      #16 for file2
    m = int(rows[index][time_row][14] + rows[index][time_row][15])
    s = int(rows[index][time_row][17] + rows[index][time_row][18])
    timer__ = h * 3600 + m * 60 + s
    return timer__


def open_order_check():
    pos = 'close'
    order = None
    indicators = rows[index]
    ema = float(indicators[5])#ema200
    rsi = float(indicators[0])#0-->rsi     #16-->UO for file3, file4, eth
    price = float(indicators[1])#close
    adx = float(indicators[12])
    # date = indicators[16]    #to file2.csv

    if time_row is not None:
        date = indicators[time_row]
    else:
        date = 'date'    #to file1.csv

    if adx > 25:

        if ((rsi*29) - (adx**1.5 - 50))/30 > 64:
            print('open long order at: ', price, ' | ', date)
            pos = 'open'
            order = 'long'
            beep(1)
        elif ((rsi*29) + (50 + adx**1.5))/30 < 36:
            print('open short order at: ', price, ' | ', date)
            pos = 'open'
            order = 'short'
            beep(1)
    return pos, order, price


def close_order_check(order, p1):
    pos = 'open'
    indicators = rows[index]
    ema = float(indicators[5])
    rsi = float(indicators[0])
    price = float(indicators[1])
    adx = float(indicators[12])
    # date = indicators[16]  # to file2.csv

    if time_row is not None:
        date = indicators[time_row]
    else:
        date = 'date'    #to file1.csv


    if ( ((rsi*29) - (adx**1.5 - 50))/30 < 51 or profit_calc_(order, p1=p1, p2=price) < -4) and order == 'long':
    # if rsi < 65 and order == 'long':
        # print(rsi)
        # print(((rsi*19) - adx)/20)
        print('close long order at: ', price, ' | ', date)
        # place_order('short')
        print('profit:', profit_calc(order, p1=p1, p2=price), '%\n')
        pos = 'close'
        beep(1)
    elif (((rsi*29) + (50 + adx**1.5))/30 > 49 or profit_calc_(order, p1=p1, p2=price) < -4) and order == 'short':
    # elif rsi > 35 and order == 'short':
        print('close short order at: ', price, ' | ', date)
        # place_order('long')
        print('profit:', profit_calc(order, p1=p1, p2=price), '%\n')
        pos = 'close'
        beep(1)

    return pos


timer0 = 1
while True:

    timer1 = timer()
    if abs(timer1 - timer0) < 240:      #4min
        index += 1
        continue

    # time.sleep(90)
    pos, order, p1 = open_order_check()
    if pos == 'open':
        while True:
            if index == len(rows):
                break
            # time.sleep(90)
            if close_order_check(order, p1) == 'close':
                order_counter += 1

                timer0 = timer()
                if time_row is None:
                    timer0 = 1

                break
            index += 1
    index += 1
    if index >= len(rows):
        overallprofit = 0
        for item in list_profit:
            overallprofit += item
        print('profit:--> ', round(overallprofit, 2))
        print(order_counter)
        exit()
