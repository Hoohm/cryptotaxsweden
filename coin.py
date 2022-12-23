from tax_event import TaxEvent

def is_fiat(coin):
    return coin in ["EUR", "USD", "SEK"]

class Coin:
    def __init__(self, symbol, max_overdraft):
        self.symbol = symbol
        self.amount = 0.0
        self.cost_basis = 0.0
        self.max_overdraft = max_overdraft

    def buy(self, amount:float, price:float):
        new_amount = self.amount + amount
        self.cost_basis = (self.cost_basis * self.amount + price) / new_amount
        self.amount = new_amount

    def sell(self, amount:float, price:float) -> TaxEvent:
        amount_left = self.amount - amount
        if amount_left < -self.max_overdraft:
            raise Exception(f"Not enough coins available for {self.symbol}, {self.amount} < {amount}.")
        if amount_left < 0.0:
            amount_left = 0.0
        tax_event = TaxEvent(amount, self.symbol, price, self.cost_basis * amount)
        self.amount = amount_left
        return tax_event

    @staticmethod
    def is_fiat(symbol):
        return symbol in ["EUR", "USD", "SEK"]