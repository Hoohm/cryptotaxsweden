import datetime

from tax_event import TaxEvent

class Coin:
    verbosity = 1 # for debugging
    amount = 0.0
    cost_basis = 0.0

    def __init__(self, symbol, max_overdraft):
        self.symbol = symbol
        self.max_overdraft = max_overdraft

    def __str__(self):
        s = self.symbol.ljust(8) + str(round(self.amount, 5)).ljust(12) + str(round(self.cost_basis, 2)).ljust(18) + (str(round(self.amount * self.cost_basis, 2)))
        return s

    def buy(self, amount:float, price:float, date:datetime):
        new_amount = self.amount + amount
        s = str(date) + ': ACQUIRED'.ljust(12) + str(round(amount, 6)).ljust(11) + self.symbol.ljust(7) + ('(' + str(price) + ' SEK)').ljust(22) \
+ ('tot. ' + self.symbol + ': ').ljust(12) + str(round(new_amount, 6)).ljust(10) + ('(' + str(round(self.cost_basis * self.amount + price, 2)) + ' SEK)').ljust(18) \
+ 'cost basis: ' + (str(round(self.cost_basis * self.amount + price, 2)) + ' / ' + str(round(new_amount, 2))).ljust(17) + ' = ' \
+ (str(round((self.cost_basis * self.amount + price) / new_amount, 2)) + ' SEK').ljust(20)
        if self.verbosity > 0: #and self.symbol[:3] == 'DOT':
            print(s)

        self.cost_basis = (self.cost_basis * self.amount + price) / new_amount
        self.amount = new_amount

    def sell(self, amount:float, price:float, date:datetime) -> TaxEvent:
        s = str(date) + ': SOLD'.ljust(12) + str(round(amount, 6)).ljust(11) + self.symbol.ljust(7) + ('@ ' + str(round(price / amount, 2)) + ' SEK/' + self.symbol).ljust(22) \
+ ('cost basis: ' + str(round(self.cost_basis, 2)) + ' SEK').ljust(40)
        s += 'PROFIT' if price / amount > self.cost_basis else 'LOSS'
        s += ': ' + str(round(amount, 10)) + ' * ' + str(round(price / amount, 2)) + ' - ' + str(round(amount, 10)) + ' * ' + str(round(self.cost_basis, 2)) + ' = ' \
+ str(round(price - amount * self.cost_basis, 2)) + ' SEK'
        if self.verbosity > 0: # and self.symbol[:3] == 'DOT':
            print(s)

        amount_left = self.amount - amount
        if amount_left < -self.max_overdraft:
            raise Exception(f"Not enough coins available for {self.symbol}, {self.amount} < {amount}.")
        if amount_left < 0.0:
            amount_left = 0.0
        tax_event = TaxEvent(amount, self.symbol, price, self.cost_basis * amount, date)
        self.amount = amount_left
        return tax_event

    @staticmethod
    def is_fiat(symbol):
        return symbol in ["EUR", "USD", "SEK"]