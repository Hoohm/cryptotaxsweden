import dateutil.parser
import csv
from datetime import datetime

from trades import Trade, Trades

# Reads and stores a list of the trades made in trades.csv
class ExcelReader:
    def __init__(self):
        pass

    # used by get_trades()
    def __read_usdsek_rates(self):
        rates = []
        with open('data/rates/usdsek.csv', encoding='utf-8-sig') as f:
            is_first = True
            for row in csv.reader(f, delimiter=',', quotechar='"'):
                if is_first:
                    is_first = False
                    continue
                date = dateutil.parser.parse(row[0])
                close = float(row[1])
                rates.append([date, close])
        rates.sort(key=lambda rate: rate[0])
        return rates

    # converter, used by get_trades()
    def __usd_to_sek(self, rates, wanted_date):
        prev_date = None
        prev_price = None
        for rate in rates:
            date = rate[0]
            price = rate[1]
            if prev_date and prev_date <= wanted_date and wanted_date < date:
                return prev_price
            prev_date = date
            prev_price = price
        raise Exception("Didn't find a USDSEK conversion rate for date %s" % wanted_date)

    def get_trades(self, filename, value_in_usd):
        with open(filename, encoding='utf-8-sig') as f:
            lines = [line for line in csv.reader(f, delimiter=',', quotechar='"')]

        if value_in_usd:
            usdsek = self.__read_usdsek_rates()

        def indices(col_name):
            return [index for index, col in enumerate(lines[0]) if col == col_name]

        price_field_name = 'Value in USD' if value_in_usd else 'Value in SEK'

        date_index = indices('Date')[0]
        type_index = indices('Type')[0]
        group_index = indices('Group')[0]
        buy_coin_index = indices('Cur.')[0]
        buy_amount_index = indices('Buy')[0]
        buy_value_index = indices(price_field_name)[0]
        sell_coin_index = indices('Cur.')[1]
        sell_amount_index = indices('Sell')[0]
        sell_value_index = indices(price_field_name)[1]

        trades = []
        lineno = 2
        for line in lines[1:]:
            trade = Trade(
                lineno,
                datetime.strptime(line[date_index], "%d.%m.%Y %H:%M"),
                line[type_index],
                None if line[group_index] == '-' else line[group_index],
                None if line[buy_coin_index] == '-' else line[buy_coin_index],
                None if line[buy_amount_index] == '-' else float(line[buy_amount_index]),
                None if line[buy_value_index] == '-' else float(line[buy_value_index]),
                None if line[sell_coin_index] == '-' else line[sell_coin_index],
                None if line[sell_amount_index] == '-' else float(line[sell_amount_index]),
                None if line[sell_value_index] == '-' else float(line[sell_value_index])
            )

            if value_in_usd:
                usdsek_rate = self.__usd_to_sek(usdsek, trade.date)
                if trade.buy_value:
                    trade.buy_value *= usdsek_rate
                if trade.sell_value:
                    trade.sell_value *= usdsek_rate
            trades.append(trade)
            lineno += 1

        trades.reverse()
        trades.sort(key=lambda x: x.date)

        return Trades(trades)