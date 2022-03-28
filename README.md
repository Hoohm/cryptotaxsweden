# Swedish cryptocurrency tax reporting script

## About
This is a tool to convert your cryptocurrency trade history to the K4 documents needed
for tax reporting to Skatteverket.

This script can generate files which are compatible with Skatteverket. There is either 
PDF output for printing and sending by mail or SRU-output which can be imported on 
skatteverket.se.

## Usage
* download transaction data: https://www.coinbase.com/reports
* import transaction data: https://cointracking.info/import/coinbase/
* download cointracking transaction data as comma-separated CVS: https://cointracking.info/trade_prices.php
* save as `data/trades.csv`
* enter personal details in `data/personal_details.json`
* run `python report.py 2021 --simplified-k4 --rounding-report --rounding-report-threshold=1 --format=sru`
* check output for errors
* test the generated sru files (in the out folder) for errors at https://www.skatteverket.se/filoverforing
* submit sru file to Skatteverket

## Test
You can use `data/trades_test.csv` to test the script. The file contains Skatteverkets own example (found here:
https://skatteverket.se/privat/skatter/vardepapper/andratillgangar/kryptovalutor.4.15532c7b1442f256bae11b60.html)
* check that trades in the file corresponds to the example
* run `python report.py 2021 --simplified-k4 --rounding-report --rounding-report-threshold=1 --format=sru --trades="data/trades_test.csv" --coin-report`
* check that profit, loss, and tax in the output under Section D is correct
* check that `out/coin_report.csv` has the correct cost basis ("omkostnadsbelopp")

## Setup
Python 3.6 is required.
```
pip install -r requirements.txt
```

## Input data
### data/personal_details.json
Make sure to save the file in UTF-8 format. On Windows you can install Notepad++ to make this easier.

### data/trades.csv
To get the data for this file you first need to have your complete trade history
on [cointracking.info](https://cointracking.info?ref=D611015). Then go to the
Trade Prices-page and download a CSV report (comma separated version) from that
page and store it at`data/trades.csv`.

## Limitations
The sru format is currently limited in that it doesn't allow
decimals, this is a limitation with skatteverket.se. The
recommendation from Skatteverket is to round to whole numbers
even if that results in 0 BTC or similar being reported and then
report what roundings have been done under Övriga Upplysningar.

The script can now generate a rounding report which can be
pasted in Övriga Upplysningar. Skatteverket limits the size of
this field to 999 characters so it is best to combine this with
doing a simplified K4 report to reduce the number of lines which
has to be reported in the K4.

## Running
### Options

```
usage: report.py [-h] [--trades TRADES] [--out OUT] [--format {pdf,sru}]
                 [--decimal-sru]
                 [--exclude-groups [EXCLUDE_GROUPS [EXCLUDE_GROUPS ...]]]
                 [--coin-report] [--simplified-k4] [--rounding-report]
                 [--rounding-report-threshold ROUNDING_REPORT_THRESHOLD]
                 [--cointracking-usd]
                 year

Swedish cryptocurrency tax reporting script

positional arguments:
  year                  Tax year to create report for

optional arguments:
  -h, --help            show this help message and exit
  --trades TRADES       Read trades from csv file
  --out OUT             Output folder
  --format {pdf,sru}    The file format of the generated report
  --decimal-sru         Report decimal amounts in sru mode (not supported by
                        Skatteverket yet)
  --exclude-groups [EXCLUDE_GROUPS [EXCLUDE_GROUPS ...]]
                        Exclude cointracking group from report
  --coin-report         Generate report of remaining coins and their cost
                        basis at end of year
  --simplified-k4       Generate simplified K4 with only two line per coin
                        type (aggregated profit and loss).
  --rounding-report     Generate report of roundings done which can be pasted
                        in Ovriga Upplysningar, the file will be put in the
                        out folder.
  --rounding-report-threshold ROUNDING_REPORT_THRESHOLD
                        The number of percent difference required for an
                        amount to be included in the report.
  --cointracking-usd    Use this flag if you have configured cointracking
                        calculate prices in USD. Conversion from USD to SEK
                        will then be done by this script instead.
  --max-overdraft MAX_OVERDRAFT
                        The maximum overdraft to allow for each coin, at the
                        event of an overdraft the coin balance will be set to
                        zero.
```

### Example
#### Generate a simplified report for 2017 in sru format.
```
python report.py 2017 --simplified-k4
```

#### Generate a simplified report for 2017 in sru format with a rounding report with threshold of 1%.
```
python report.py 2017 --simplified-k4 --rounding-report --rounding-report-threshold=1
```

#### Merging the generated pdf files
Merging the pdf files can be done with Ghostscript. It might make printing a bit easier.

```
cd out
gs -q -dNOPAUSE -dBATCH -sDEVICE=pdfwrite -sOutputFile=merged.pdf k4_no*.pdf
```
