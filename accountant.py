import os 
import datetime

from tax_event import TaxEvent
from wallets import Wallet, Wallets
from trade_sheet import TradeSheet
from personal_details import PersonalDetails
from k4page import K4Page, K4Section
from format import Format

class Accountant:
    def __init__(self, cli_options):
        self.cli_options = cli_options
        self.wallets = Wallets(cli_options.max_overdraft, 'SEK')
        self.personal_details = PersonalDetails()
        self.tradesheet = TradeSheet(cli_options.trades, cli_options.cointracking_usd)
        self.tax_events = []

    def compute_tax(self):
        exclude_groups = self.cli_options.exclude_groups if self.cli_options.exclude_groups else []
        
        # set tax timeperiod
        from_date = datetime.datetime(year=self.cli_options.year,month=1,day=1,hour=0, minute=0)
        to_date = datetime.datetime(year=self.cli_options.year,month=12,day=31,hour=23, minute=59)

        for trade in self.tradesheet.trades:
            if trade.date > to_date:
                break
            if trade.group in exclude_groups:
                continue

            try:
                # Execute trade with your wallets
                tax_event = trade.execute(self.wallets)
                if tax_event and tax_event.date >= from_date:
                    self.tax_events.append(tax_event)

            except Exception as e:
                print(f"ERROR: Exception for trade at line {trade.lineno} in trades.csv: {e}")
                return None

        print(f'INFO: Parsed {len(self.tradesheet.trades)} total transactions')
        print(f'INFO: Printing wallet:\n{self.wallets}')
        print()

    def write_report(self):
        if self.tax_events is None:
            print(f"WARNING: No tax events found")

        if self.cli_options.coin_report:
            self.create_coin_report()

        self.create_k4_report()

    # used by create_k4_report() if self.cli_options.simplified_k4
    def __aggregate_per_coin(self):
        aggregate_tax_events = {}
        for tax_event in self.tax_events:
            if tax_event.name not in aggregate_tax_events:
                aggregate_tax_events[tax_event.name] = (TaxEvent(0.0, tax_event.name, 0.0, 0.0, tax_event.date), TaxEvent(0.0, tax_event.name, 0.0, 0.0, tax_event.date))
            (aggregate_profit_tax_event, aggregate_loss_tax_event) = aggregate_tax_events[tax_event.name]
            if tax_event.profit() > 0.0:
                aggregate_profit_tax_event.amount += tax_event.amount
                aggregate_profit_tax_event.income += tax_event.income
                aggregate_profit_tax_event.cost += tax_event.cost
            else:
                aggregate_loss_tax_event.amount += tax_event.amount
                aggregate_loss_tax_event.income += tax_event.income
                aggregate_loss_tax_event.cost += tax_event.cost

        sorted_aggregate_events = list(aggregate_tax_events.items())
        sorted_aggregate_events.sort()
        new_tax_events = []
        for (name, (aggregate_profit_tax_event, aggregate_loss_tax_event)) in sorted_aggregate_events:
            if (aggregate_profit_tax_event.amount > 0.0):
                new_tax_events.append(aggregate_profit_tax_event)
            if (aggregate_loss_tax_event.amount > 0.0):
                new_tax_events.append(aggregate_loss_tax_event)

        self.tax_events = new_tax_events

    # used by create_k4_report()
    def __rounding_report(self):
        threshold = float(self.cli_options.rounding_report_threshold) / 100.0
        report_filename = os.path.join(self.cli_options.out, "rounding_report.txt")

        with open(report_filename, 'w', encoding='utf-8') as f:
            print(f'INFO: writing to {report_filename}')
            f.write(f"Decimaler stöds ej för bilaga K4 på skatteverket.se.\n")
            f.write(f"Här är en lista på avrundningar där det avrundade antalet skiljer sig mer än {str(threshold*100)[:4]}% från det egentliga antalet:\n")
            f.write(f"\n")
            for tax_event in self.tax_events:
                original = tax_event.amount
                rounded = round(tax_event.amount)
                if abs(rounded - original) / original > threshold:
                    f.write(f"{original} {tax_event.name} har avrundats till {rounded} {tax_event.name}\n")

        if os.stat(report_filename).st_size > 999:
            raise Exception("Rounding report is longer than 999 characters (the limit on skatteverket.se), consider increasing the threshold --rounding-report-threshold and doing a simplified K4 --simplified-k4.")

    # used by create_k4_report()
    def __convert_to_integer_amounts(self):
        new_events = []
        for tax_event in self.tax_events:
            tax_event.amount = round(tax_event.amount)
            new_events.append(tax_event)
        self.tax_events = new_events

    # used by create_k4_report()
    def __convert_to_integer_amounts_with_prefix(self, precision_loss_tolerance=0.1):
        prefixes = [("", 1.0), ("milli", 1000.0), ("micro", 1000000.0)]

        # Check which coins need to be modified to not lose to much precision.
        coin_prefixes = {}
        coins = set([x.name for x in self.tax_events])
        for coin in coins:
            if not Wallet.is_fiat(coin):
                for (prefix, factor) in prefixes:
                    loss = max([abs(round(factor*x.amount) - factor*x.amount) / (factor*x.amount)
                                for x in self.tax_events if x.name == coin])
                    if loss < precision_loss_tolerance:
                        break
                else:
                    raise Exception("No prefix with low enough loss found")
                coin_prefixes[coin] = (prefix, factor)

        # Convert amount to integer
        new_events = []
        for tax_event in self.tax_events:
            if tax_event.name in coin_prefixes:
                tax_event.amount = round(coin_prefixes[tax_event.name][1] * tax_event.amount)
                tax_event.name = f"{coin_prefixes[tax_event.name][0]}{tax_event.name}"
            else:
                tax_event.amount = round(tax_event.amount)
            new_events.append(tax_event)

        self.tax_events = new_events

    # used by create_k4_report()
    def __convert_sek_to_integer_amounts(self):
        new_events = []
        for tax_event in self.tax_events:
            tax_event.income = round(tax_event.income)
            tax_event.cost = round(tax_event.cost)
            new_events.append(tax_event)
        self.tax_events = new_events

    # used by create_k4_report()
    def __generate_k4_pages(self):
        def generate_section(events):
            lines = []
            num_sums = [0, 0, 0, 0]
            for event in events:
                k4_fields = event.k4_fields()
                line = []
                for (field_index, field) in enumerate(k4_fields):
                    if field_index > 3:
                        line.append(str(field) if field else None)
                    else:
                        line.append(str(field) if field else "0")
                    if field_index > 1 and field:
                        num_sums[field_index-2] += field
                lines.append(line)
            sums = [str(sum) if sum > 0 else None for sum in num_sums]
            return K4Section(lines, sums)

        fiat_events = [x for x in self.tax_events if Wallet.is_fiat(x.name)]
        crypto_events = [x for x in self.tax_events if not Wallet.is_fiat(x.name)]

        pages = []
        page_number = 1
        while True:
            if self.stock_tax_events:
                section_a_events = self.stock_tax_events[(page_number-1)*9:page_number*9]
            else:
                section_a_events = []
            section_c_events = fiat_events[(page_number-1)*7:page_number*7]
            section_d_events = crypto_events[(page_number-1)*7:page_number*7]
            if not section_a_events and not section_c_events and not section_d_events:
                break
            section_a = generate_section(section_a_events)
            section_c = generate_section(section_c_events)
            section_d = generate_section(section_d_events)
            pages.append(K4Page(self.cli_options.year, self.personal_details, page_number,
                                section_a, section_c, section_d))
            page_number += 1
        return pages

    # used by create_k4_report() if self.cli_options.format == Format.sru
    def __generate_k4_sru(self, pages):
        destination_folder = self.cli_options.out

        # Generate info.sru
        lines = []
        lines.append("#DATABESKRIVNING_START")
        lines.append("#PRODUKT SRU")
        lines.append("#FILNAMN BLANKETTER.SRU")
        lines.append("#DATABESKRIVNING_SLUT")
        lines.append("#MEDIELEV_START")
        lines.append(f"#ORGNR {self.personal_details.personnummer}")
        lines.append(f"#NAMN {self.personal_details.namn}")
        lines.append(f"#POSTNR {self.personal_details.postnummer}")
        lines.append(f"#POSTORT {self.personal_details.postort}")
        lines.append("#MEDIELEV_SLUT")
        lines.append("")

        with open(os.path.join(destination_folder, "info.sru"), "w", encoding="iso-8859-1") as f:
            print('INFO: writing to out\info.sru')
            f.write("\n".join(lines))
            
        # Generate blanketter.sru
        lines = []
        for page in pages:
            lines.extend(page.generate_sru_lines())
        lines.append("#FIL_SLUT")
        lines.append("")
        if not os.path.exists(destination_folder):
            os.makedirs(destination_folder)
        with open(os.path.join(destination_folder, "blanketter.sru"), "w", encoding="iso-8859-1") as f:
            print('INFO: writing to out\\blanketter.sru')
            f.write("\n".join(lines))

    # used by create_k4_report() if self.cli_options.format == Format.pdf
    def __generate_k4_pdf(self, pages, destination_folder):
        for page in pages:
            page.generate_pdf(destination_folder)

    # used by create_k4_report()
    def __output_totals(self):
        crypto_tax_events = [x for x in self.tax_events if not Wallet.is_fiat(x.name)]
        fiat_tax_events = [x for x in self.tax_events if Wallet.is_fiat(x.name)]
        
        print()
        if self.stock_tax_events:
            stock_total_profit = sum([x.profit() if x.profit() > 0 else 0 for x in self.stock_tax_events])
            stock_total_loss = sum([-x.profit() if x.profit() < 0 else 0 for x in self.stock_tax_events])
            print("Section A")
            print(f"  Summed profit (box 7.4): {stock_total_profit}")
            print(f"  Summed loss (box 8.3): {stock_total_loss}")
        fiat_total_profit = sum([x.profit() if x.profit() > 0 else 0 for x in fiat_tax_events])
        fiat_total_loss = sum([-x.profit() if x.profit() < 0 else 0 for x in fiat_tax_events])
        print("Section C")
        print(f"  Summed profit (box 7.2): {fiat_total_profit}")
        print(f"  Summed loss (box 8.1): {fiat_total_loss}")
        crypto_total_profit = sum([x.profit() if x.profit() > 0 else 0 for x in crypto_tax_events])
        crypto_total_loss = sum([-x.profit() if x.profit() < 0 else 0 for x in crypto_tax_events])
        print("Section D")
        print(f"  Summed profit (box 7.5): {crypto_total_profit}")
        print(f"  Summed loss (box 8.4): {crypto_total_loss}")
        print(f"  Section D Tax: {round(0.3*(crypto_total_profit - 0.7*crypto_total_loss))}")

    # creates a coin report
    # called by Accountant::write_report() if cli_options.coin_report
    def create_coin_report(self):        
        coin_report_filename = os.path.join(self.cli_options.out, "coin_report.csv") if self.cli_options.coin_report else None
        with open(coin_report_filename, "w") as f:
            print(f'INFO: writing to {coin_report_filename}')
            f.write(f"{'Amount'.ljust(14)}{'Coin'.ljust(8)}{'Cost basis'.ljust(10)}\n")
            wallets = [w for (_, w) in self.wallets.wallets.items() if w.amount > 1e-9]
            wallets.sort(key=lambda w: w.symbol)
            for w in wallets:
                f.write(f"{str(w.amount)[:12].ljust(14)}{str(w.symbol).ljust(8)}{str(w.cost_basis)[:8].ljust(10)}\n")

    # creates a K4 report
    # called by Accountant::write_report()
    def create_k4_report(self):
        if self.cli_options.simplified_k4:
            self.__aggregate_per_coin()

        if self.cli_options.format == Format.sru and not self.cli_options.decimal_sru:
            if self.cli_options.rounding_report:
                self.__rounding_report()
            self.__convert_to_integer_amounts()
        self.__convert_sek_to_integer_amounts()

        self.stock_tax_events = TaxEvent.read_stock_tax_events_from("data/stocks.json") if os.path.exists("data/stocks.json") else None
        pages = self.__generate_k4_pages()
        if self.cli_options.format == Format.sru:
            self.__generate_k4_sru(pages)
        elif self.cli_options.format == Format.pdf:
            self.__generate_k4_pdf(pages)

        self.__output_totals()
