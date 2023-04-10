import time
import requests
import smtplib
from datetime import datetime
# from beep import beep
import csv
import threading
from tqdm import trange

# all_processes = 1000
time_index = 20


def fr_bot(upper_enter_rsi, upper_exit_rsi, ratio):
    ratio = ratio/10
    leverage = 10
    index = 0  # The index that under consideration
    """""
    1 beep: open order
    3 beep: error
    """""
    order_counter = 0

    file = open('file2.csv')
    csvreader = csv.reader(file)
    rows = []
    for row in csvreader:
        rows.append(row)
    # print('records:', len(rows), '\n')
    del rows[0]

    list_profit = []

    def profit_calc(order, p1, p2, leverage=leverage):
        if order == 'long':
            profit = ((p2 - p1) / p2) * 100
        else:
            profit = ((p1 - p2) / p1) * 100
        list_profit.append(profit * leverage)
        return round(profit * leverage, 2)

    def timer():
        h = int(rows[index][time_index][11] + rows[index][time_index][12])
        m = int(rows[index][time_index][14] + rows[index][time_index][15])
        s = int(rows[index][time_index][17] + rows[index][time_index][18])
        timer__ = h * 3600 + m * 60 + s
        return timer__

    def open_order_check():
        pos = 'close'
        order = None
        indicators = rows[index]
        ema = float(indicators[5])  # ema200
        rsi = float(indicators[0])  # rsi
        price = float(indicators[1])  # close
        date = indicators[time_index]  # to file2.csv
        adx = float(indicators[12])
        # date = indicators[20]    #to file_5min.csv
        # date = 'date'    #to file1.csv

        if adx > 25:
            if ((rsi*29) - (adx**ratio - 50))/30 > upper_enter_rsi:
                # print('open long order at: ', price, ' | ', date)
                pos = 'open'
                order = 'long'
                # beep(1)
            elif ((rsi*29) + (50 + adx**ratio))/30 < 100 - upper_enter_rsi:
                # print('open short order at: ', price, ' | ', date)
                pos = 'open'
                order = 'short'
                # beep(1)
        return pos, order, price

    def close_order_check(order, p1):
        pos = 'open'
        indicators = rows[index]
        ema = float(indicators[5])
        rsi = float(indicators[0])
        price = float(indicators[1])
        date = indicators[time_index]  # to file2.csv
        adx = float(indicators[12])
        # date = indicators[20]    #to file_5min.csv
        # date = 'date'    #to file1.csv

        if ((rsi * 29) - (adx ** ratio - 50)) / 30 < upper_exit_rsi and order == 'long':
            # print('close long order at: ', price, ' | ', date)
            profit_calc(order, p1=p1, p2=price)
            pos = 'close'
            # beep(1)
        elif ((rsi * 29) + (50 + adx ** ratio)) / 30 > 100 - upper_exit_rsi and order == 'short':
            # print('close short order at: ', price, ' | ', date)
            profit_calc(order, p1=p1, p2=price)
            pos = 'close'
            # beep(1)
        return pos
    timer0 = 1
    while True:

        timer1 = timer()
        if abs(timer1 - timer0) < 240:        #4min
            index += 1
            continue

        # time.sleep(90)
        pos, order, p1 = open_order_check()
        if pos == 'open':
            while True:
                if index >= len(rows)-10:
                    break
                # time.sleep(90)
                if close_order_check(order, p1) == 'close':
                    order_counter += 1
                    timer0 = timer()
                    break
                index += 1
        index += 1
        if index >= len(rows)-10:
            overallprofit = 0
            for item in list_profit:
                overallprofit += item
            # print('profit:--> ', round(overallprofit, 2))
            # print(round(overallprofit, 2))

            if overallprofit > 50:

                list_result.append((upper_enter_rsi, 100-upper_enter_rsi, upper_exit_rsi, 100-upper_exit_rsi, ratio
                                    , (round(overallprofit, 2), order_counter)))
                # print(overallprofit, order_counter)
            return round(overallprofit, 2)

list_result = []


def processing(upper_enter_rsi, upper_exit_rsi, ratio):
    counter = 0
    counter_v = 1
    for i in trange(upper_enter_rsi[0], upper_enter_rsi[1], desc='1st loop'):
        for j in trange(upper_exit_rsi[0], upper_exit_rsi[1], desc='2nd'):
            for k in range(ratio[0], ratio[1]):
                if i > j:
                    if 100 - i < 100 - j:
                        t_1 = threading.Thread(target=fr_bot, args=(i, j, k))
                        # t_1.start()
                        t_1.run()
                        # counter += 1
                        # if counter > 70:
                        #     while True:
                        #         if len(list_result) > 70 * counter_v:
                        #             counter = 0
                        #             counter_v += 1
                        #             break
                        #         time.sleep(1)
processing([60, 80], [50, 70], [10, 22])
# while True:
#     if len(list_result) == all_processes:     #all processes finished
#         break

print(list_result)
# list_result.append((i, 29, (fr_bot(i, 29))))

