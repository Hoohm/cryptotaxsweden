from tax_event import TaxEvent

class Wallets:
    wallets = {}
    def __init__(self, max_overdraft, native_currency):
        self.max_overdraft = max_overdraft
        self.native_currency = native_currency

    def __str__(self):
        s = 'NAME'.ljust(8) + 'AMOUNT'.ljust(12) + 'AVG. COST BASIS (SEK)'.ljust(24) + 'TOT. COST BASIS (SEK)\n'
        for wallet in self.wallets.values():
            s += str(wallet) + '\n'
        s += 'Summed cost basis: ' + str(int(self.get_total_cost_basis())) + ' SEK'
        return s

    def get_buy_wallet(self, buy_coin_str):
        if Wallet.is_fiat(buy_coin_str):
            buy_wallet = None
        elif buy_coin_str not in self.wallets:
            self.wallets[buy_coin_str] = Wallet(buy_coin_str, self.max_overdraft)
            buy_wallet = self.wallets[buy_coin_str]
        else:
            buy_wallet = self.wallets[buy_coin_str]
        return buy_wallet

    def get_sell_wallet(self, sell_coin_str):
        if  Wallet.is_fiat(sell_coin_str):
            sell_wallet = None
        elif sell_coin_str in self.wallets:
            sell_wallet = self.wallets[sell_coin_str]
        else:
            Exception(f"Attempting to sell {sell_coin_str} which has not been bought yet")
        return sell_wallet
    
    # calculates what you have spent to buy your coins in SEK, not including commission, spread, etc.
    def get_total_cost_basis(self):
        tot_cb = 0
        for w in self.wallets.values():
            tot_cb += w.amount * w.cost_basis
        return tot_cb

class Wallet:
    verbosity = 1 # for debugging
    amount = 0.0
    cost_basis = 0.0
    native_currency = 'SEK' # TODO: move to accountant

    def __init__(self, symbol, max_overdraft):
        self.symbol = symbol
        self.max_overdraft = max_overdraft

    def __str__(self):
        s = self.symbol.ljust(8) + str(round(self.amount, 5)).ljust(12) + str(round(self.cost_basis, 2)).ljust(24) + (str(round(self.amount * self.cost_basis, 2)))
        return s

    @staticmethod
    def is_fiat(symbol):
        return symbol in ["EUR", "USD", "SEK"]


    def buy(self, amount:float, price:float, date):
        new_amount = self.amount + amount
        s = str(date) + ': ACQUIRED'.ljust(12) + str(round(amount, 6)).ljust(11) + self.symbol.ljust(7) + ('(' + str(price) + ' SEK)').ljust(22) \
+ ('tot. ' + self.symbol + ': ').ljust(12) + str(round(new_amount, 6)).ljust(10) + ('(' + str(round(self.cost_basis * self.amount + price, 2)) + ' SEK)').ljust(18) \
+ 'cost basis: ' + (str(round(self.cost_basis * self.amount + price, 2)) + ' / ' + str(round(new_amount, 2))).ljust(17) + ' = ' \
+ (str(round((self.cost_basis * self.amount + price) / new_amount, 2)) + ' SEK').ljust(20)
        if self.verbosity > 0: #and self.symbol[:3] == 'DOT':
            print(s)

        self.cost_basis = (self.cost_basis * self.amount + price) / new_amount
        self.amount = new_amount

    def sell(self, amount:float, price:float, date) -> TaxEvent:
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
