import os 
import datetime

from tax_event import TaxEvent
from trades import Trade
from excel_reader import ExcelReader
from coin import Coin
from personal_details import PersonalDetails
from report_writer import ReportWriter

class Accountant:
    def __init__(self, cli_options):
        self.verbosity = 2
        self.cli_options = cli_options
        self.native_currency = 'SEK'

        self.tax_events = []
        self.wallet = {}
        self.stock_tax_events = TaxEvent.read_stock_tax_events_from("data/stocks.json") if os.path.exists("data/stocks.json") else None

        self.personal_details = PersonalDetails()
        self.excel_reader = ExcelReader()
        self.report_writer = ReportWriter(cli_options)
        
        self.coin_report_filename = os.path.join(self.cli_options.out, "coin_report.csv") if self.cli_options.coin_report else None
        self.exclude_groups = self.cli_options.exclude_groups if self.cli_options.exclude_groups else []
        self.trades = self.excel_reader.get_trades(self.cli_options.trades, self.cli_options.cointracking_usd)

    # returns the coin we are buying in a trade
    # used by compute_tax()
    def __get_buy_coin(self, trade: Trade):  
        # do not put fiat money in our wallet
        if Coin.is_fiat(trade.buy_coin):
            return None

        if trade.buy_coin not in self.wallet:
            self.wallet[trade.buy_coin] = Coin(trade.buy_coin, self.cli_options.max_overdraft)

        return self.wallet[trade.buy_coin]

    # returns the coin we are selling in a trade
    # used by compute_tax()
    def __get_sell_coin(self, trade: Trade):
        # do not expect fiat in our wallet
        if Coin.is_fiat(trade.sell_coin):
            return None

        if trade.sell_coin not in self.wallet:
            raise Exception(f"ERROR: attempting to sell {trade.sell_coin} which has not been bought yet")

        return self.wallet[trade.sell_coin]

    def compute_tax(self):
        from_date = datetime.datetime(year=self.cli_options.year,month=1,day=1,hour=0, minute=0)
        to_date = datetime.datetime(year=self.cli_options.year,month=12,day=31,hour=23, minute=59)

        len_c = len(self.trades.trades)
        self.trades.purge_anomalies()
        len_d = len(self.trades.trades)

        len_a = len(self.trades.trades)
        self.trades.purge_duplicates()
        len_b = len(self.trades.trades)

        for trade in self.trades.trades:
            if trade.date > to_date:
                break
            if trade.group in self.exclude_groups:
                continue

            try:
                if trade.type == 'Trade':
                    print(trade) if self.verbosity > 1 else None
                    buy_coin = self.__get_buy_coin(trade)
                    sell_coin = self.__get_sell_coin(trade)

                    if trade.sell_coin == self.native_currency:
                        value_sek = trade.sell_value
                    else:
                        value_sek = trade.buy_value

                    if buy_coin:
                        buy_coin.buy(trade.buy_amount, value_sek)
                    if sell_coin:
                        tax_event = sell_coin.sell(trade.sell_amount, value_sek)
                        if trade.date >= from_date:
                            self.tax_events.append(tax_event)
                            print('INFO: transaction is a taxable event') if self.verbosity > 1 else None
                    print() if self.verbosity > 1 else None

                elif trade.type == 'Spend' or trade.type == 'Withdrawal':
                    print(trade) if self.verbosity > 1 else None
                    sell_coin = self.__get_sell_coin(trade)
                    if sell_coin:
                        tax_event = sell_coin.sell(trade.sell_amount, trade.sell_value)
                        if trade.date >= from_date:
                            self.tax_events.append(tax_event)
                            print('INFO: transaction is a taxable event') if self.verbosity > 1 else None
                    print() if self.verbosity > 1 else None

                elif trade.type == 'Mining' or trade.type == 'Staking':
                    buy_coin = self.__get_buy_coin(trade)
                    if buy_coin:
                        buy_coin.buy(trade.buy_amount, trade.buy_value)

                elif trade.type == 'Gift/Tip' or trade.type == 'Deposit':
                    buy_coin = self.__get_buy_coin(trade)
                    if buy_coin:
                        buy_coin.buy(trade.buy_amount, 0.0)

                else:
                    raise Exception('ERROR: trade type not supported')

            except Exception as e:
                print(f"ERROR: Exception at line {trade.lineno} in trades csv-file: {e}")
                return None

        print("INFO: Purged", len_a - len_b, "duplicates in report.") if self.verbosity > 0 else None
        print("INFO: Purged", len_c - len_d, "anomalies in report.") if self.verbosity > 0 else None
        print('INFO: Found', len(self.trades.trades), 'total transactions')  if self.verbosity > 0 else None

    def write_report(self):
        if self.tax_events is None:
            print(f"WARNING: No tax events found")
            exit(1)

        if self.cli_options.coin_report:
            self.report_writer.create_coin_report(self.coin_report_filename, self.wallet)

        self.report_writer.create_k4_report(self.tax_events, self.stock_tax_events, self.personal_details)
