from datetime import datetime

class Trade:
    def __init__(self, lineno, date:datetime, type, group,
                 buy_coin_str:str, buy_amount, buy_value,
                 sell_coin_str:str, sell_amount, sell_value):
        self.verbosity = 1
        self.lineno = lineno
        self.date = date
        self.type = type
        self.group = group
        self.buy_coin_str = buy_coin_str # currency that is bought, ex. 'BTC'
        self.buy_amount = buy_amount # amount that is bought, ex. 0.000001
        self.buy_value = buy_value # value in native currency, ex. 10 (SEK)
        self.sell_coin_str = sell_coin_str # currency that is sold, ex. 'USD'
        self.sell_amount = sell_amount # amount that is sold, ex. 1
        self.sell_value = sell_value # value in native currency, ex. 11 (SEK)

    def __str__(self):
        s = '+-- Transaction --------------------------------+\n' + \
            '| date\t\t' + str(self.date).ljust(32) + '|\n' + \
            '| type\t\t' + str(self.type).ljust(32) + '|\n' + \
            '| sell\t\t' + (str(self.sell_amount) + ' ' + str(self.sell_coin_str) + ' (' + str(self.sell_value) + ' SEK)').ljust(32) + '|\n'
        if self.buy_value != None:
            s += '| buy\t\t' + (str(self.buy_amount) + ' ' + str(self.buy_coin_str) + ' (' + str(self.buy_value) + ' SEK)').ljust(32) + '|\n'
        if self.sell_value != None and self.buy_value != None:
            s += '| cost\t\t' + (str(int(self.sell_value - self.buy_value)) + ' SEK (' + str(round(((self.sell_value - self.buy_value) / self.buy_value) * 100, 2)) + '% spread)').ljust(32) + '|\n' 
        s += '+-----------------------------------------------+'
        return s

    # performs this trade operation on a wallet
    def perform(self, wallet):
        if self.type == 'Trade':
            print(self, '\n') if self.verbosity > 1 else None #and self.buy_coin_str[:3] == 'DOT' else None
            buy_coin = wallet.get_buy_coin(self.buy_coin_str)
            sell_coin = wallet.get_sell_coin(self.sell_coin_str)

            if self.sell_coin_str == wallet.native_currency:
                value_sek = self.sell_value
            else:
                value_sek = self.buy_value

            if buy_coin:
                buy_coin.buy(self.buy_amount, value_sek, self.date)
            if sell_coin:
                tax_event = sell_coin.sell(self.sell_amount, value_sek, self.date)
                wallet.tax_events.append(tax_event)

            if not buy_coin and not sell_coin: # will happen if we trade fiat currencies
                raise Exception('Could not retreieve buy or sell coin for the trade')

        elif self.type == 'Spend' or self.type == 'Withdrawal':
            print(self, '\n') if self.verbosity > 1 else None
            sell_coin = wallet.get_sell_coin(self.sell_coin_str)
            if sell_coin:
                tax_event = sell_coin.sell(self.sell_amount, self.sell_value, self.date)
                wallet.tax_events.append(tax_event)
            else:
                raise Exception('Could not retreieve sell coin for the trade')

        elif self.type == 'Mining' or self.type == 'Staking':
            buy_coin = wallet.get_buy_coin(self.buy_coin_str)
            if buy_coin:
                buy_coin.buy(self.buy_amount, self.buy_value, self.date)
            else:
                raise Exception('Could not retreieve buy coin for the trade')

        elif self.type == 'Gift/Tip' or self.type == 'Deposit':
            buy_coin = wallet.get_buy_coin(self.buy_coin_str)
            if buy_coin:
                buy_coin.buy(self.buy_amount, 0.0, self.date)
            else:
                raise Exception('Could not retreieve buy coin for the trade')
        else:
            raise Exception('Trade type not supported')

    # used to identify duplicate trades
    def equal(self, other):
        same_date_and_type = self.date == other.date and self.type == other.type
        same_buy = self.buy_coin_str == other.buy_coin_str and self.buy_amount == other.buy_amount
        same_sell = self.sell_coin_str == other.sell_coin_str and self.sell_amount == other.sell_amount
        return same_date_and_type and (same_buy or same_sell)