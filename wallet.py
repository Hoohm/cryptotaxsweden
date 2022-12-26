from trade import Trade
from coin import Coin

class Wallet:
    def __init__(self, max_overdraft):
        self.coins = {}
        self.max_overdraft = max_overdraft
        self.native_currency = 'SEK'
        self.tax_events = []

    def __str__(self):
        s = 'NAME'.ljust(8) + 'AMOUNT'.ljust(12) + 'COST BASIS (SEK)'.ljust(18) + 'ACQUIRED FOR (SEK)\n'
        for coin in self.coins.values():
            s += str(coin) + '\n'
        s += 'Total acquisition cost: ' + str(int(self.get_total_cost_basis())) + ' SEK'
        return s

    # calculates what you have spent to buy your coins in SEK, not including commission, spread, etc.
    def get_total_cost_basis(self):
        tot_cb = 0
        for coin in self.coins.values():
            tot_cb += coin.amount * coin.cost_basis
        return tot_cb

    # takes a string ex. 'BTC', returns that Coin from the wallet
    def get_buy_coin(self, coin_str:str):
        # do not put fiat money in our wallet # TODO: Maybe revert?
        if Coin.is_fiat(coin_str):
            return None

        if coin_str not in self.coins:
            self.coins[coin_str] = Coin(coin_str, self.max_overdraft)

        return self.coins[coin_str]

    # returns the coin being sold in a trade
    def get_sell_coin(self, coin_str:str):
        # do not expect fiat in our wallet
        if Coin.is_fiat(coin_str):
            return None

        if coin_str not in self.coins:
            raise Exception(f"Attempting to sell {coin_str} which has not been bought yet")

        return self.coins[coin_str]
