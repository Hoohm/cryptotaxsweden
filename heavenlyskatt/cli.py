import argparse
import os

from heavenlyskatt.format import Format

class CommandLineInterface:
    def __init__(self):
        pass 

    def run(self):
        parser = argparse.ArgumentParser(description='Swedish cryptocurrency tax reporting script')
        parser.add_argument('year', type=int,
                            help='Tax year to create report for')
        parser.add_argument('--trades', help='Read trades from csv file')
        parser.add_argument('--info', help='Read personnal info from json')
        parser.add_argument('--out', help='Output folder', default='out')
        parser.add_argument('--format', type=Format, choices=list(Format), default=Format.sru,
                            help='The file format of the generated report')
        parser.add_argument('--decimal-sru', help='Report decimal amounts in sru mode (not supported by Skatteverket yet)', action='store_true')
        parser.add_argument('--exclude-groups', nargs='*', help='Exclude cointracking group from report')
        parser.add_argument('--coin-report', help='Generate report of remaining coins and their cost basis at end of year', action='store_true')
        parser.add_argument('--simplified-k4', help='Generate simplified K4 with only two line per coin type (aggregated profit and loss).', action='store_true')
        parser.add_argument('--rounding-report', help='Generate report of roundings done which can be pasted in Ovriga Upplysningar, the file will be put in the out folder.', action='store_true')
        parser.add_argument('--rounding-report-threshold', help='The number of percent difference required for an amount to be included in the report.', default='1')
        parser.add_argument('--cointracking-usd', help='Use this flag if you have configured cointracking calculate prices in USD. Conversion from USD to SEK will then be done by this script instead.', action='store_true')
        parser.add_argument('--max-overdraft', type=float, help='The maximum overdraft to allow for each coin, at the event of an overdraft the coin balance will be set to zero.', default=1e-9)

        self.options = parser.parse_args()

        if not os.path.isdir(self.options.out):
            os.makedirs(self.options.out)
