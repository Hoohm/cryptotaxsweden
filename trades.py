from datetime import datetime
import dateutil.parser
import csv
import json

class Trade:
    def __init__(self, lineno, date:datetime, type, group,
                 buy_coin, buy_amount, buy_value,
                 sell_coin, sell_amount, sell_value):
        self.lineno = lineno
        self.date = date
        self.type = type
        self.group = group
        self.buy_coin = buy_coin # currency that is bought, ex. BTC
        self.buy_amount = buy_amount # amount that is bought, ex. 0.000001 BTC
        self.buy_value = buy_value # value in native currency, ex. 10 SEK
        self.sell_coin = sell_coin # currency that is sold, ex. USD
        self.sell_amount = sell_amount # amount that is sold, ex. $1
        self.sell_value = sell_value # value in native currency, ex. 11 SEK

    def __str__(self):
        s = '+-- Transaction --------------------------------+\n' + \
            '| date\t\t' + str(self.date).ljust(32) + '|\n' + \
            '| type\t\t' + str(self.type).ljust(32) + '|\n' + \
            '| sell\t\t' + (str(self.sell_amount) + ' ' + str(self.sell_coin) + ' (' + str(self.sell_value) + ' SEK)').ljust(32) + '|\n'
        if self.buy_value != None:
            s += '| buy\t\t' + (str(self.buy_amount) + ' ' + str(self.buy_coin) + ' (' + str(self.buy_value) + ' SEK)').ljust(32) + '|\n'
        if self.sell_value != None and self.buy_value != None:
            s += '| cost\t\t' + (str(int(self.sell_value - self.buy_value)) + ' SEK (' + str(round(((self.sell_value - self.buy_value) / self.buy_value) * 100, 2)) + '% spread)').ljust(32) + '|\n' 
        s += '+-----------------------------------------------+'
        return s

    # used to identify duplicate trades
    def equal(self, other):
        return self.date == other.date and \
            self.buy_coin == other.buy_coin and \
            self.buy_amount == other.buy_amount and \
            self.type == other.type

class Trades:
    def __init__(self, trades):
        self.trades = trades

    # adds a fake sale transaction to see effect on tax 
    def inject_sell(self):
        pass 
    
    # removes duplicate entries in the list
    def purge_duplicates(self):
        duplicate_count = 0
        tmp_trades = []
        for i in range(len(self.trades)):
            # if next trade is equal to current, do not add current, otherwise do add.
            if i + 1 < len(self.trades) and not self.trades[i].equal(self.trades[i+1]):
                tmp_trades.append(self.trades[i])
            #elif i + 1 < len(self.trades) and False:
            #    print("Did not add following:")
            #    print(self.trades[i])
            #    print("Because it was same as:")
            #    print(self.trades[i+1])
            #    print()

            # ... always add last trade
            if i + 1 == len(self.trades):
                tmp_trades.append(self.trades[i])
        self.trades = tmp_trades
