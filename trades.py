from datetime import datetime

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
        tmp_trades = []
        for i in range(len(self.trades)):
            # if next trade is equal to current, do not add current, otherwise do add.
            if i + 1 < len(self.trades) and not self.trades[i].equal(self.trades[i+1]):
                tmp_trades.append(self.trades[i])
            # ... always add last trade
            if i + 1 == len(self.trades):
                tmp_trades.append(self.trades[i])
        self.trades = tmp_trades

    # returns list of duplicate trades
    def get_duplicates(self):
        duplicates = []
        for i in range(len(self.trades)):
            # if next trade is equal to current, count as duplicate
            if i + 1 < len(self.trades) and self.trades[i].equal(self.trades[i+1]):
                duplicates.append(self.trades[i])
        return duplicates

    def purge_anomalies(self):
        tmp_trades = []
        for trade in self.trades:
            # keep trade if spread is < 40 % and > 0 % or undefined
            if trade.sell_value != None and trade.buy_value != None:
                spread = ((trade.sell_value - trade.buy_value) / trade.buy_value) * 100
                if spread < 40 and spread > 0:
                    tmp_trades.append(trade)
            else:
                tmp_trades.append(trade)
        self.trades = tmp_trades

    # returns list of trades where cost / spread is abnormal
    def get_anomalies(self):
        anomalies = []
        for trade in self.trades:
            # append if spread is > 40 % or < 0 %
            if trade.sell_value != None and trade.buy_value != None:
                spread = ((trade.sell_value - trade.buy_value) / trade.buy_value) * 100
                if spread > 40 or spread < 0:
                    anomalies.append(trade)
            else:
                anomalies.append(trade)
        return Trades(anomalies)