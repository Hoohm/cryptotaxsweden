# Swedish cryptocurrency tax reporting script
## About
This is a tool to convert your cryptocurrency trade history to the K4 documents needed
for tax reporting to Skatteverket.

This script can generate files which are compatible with Skatteverket. There is either 
PDF output for printing and sending by mail or SRU-output which can be imported on 
skatteverket.se.

## Requirements
* a coinbase account where you have made all your transactions
* a cointracking account (free)
* git, python3, and pip installed on your computer

## Setup
1. Clone the repo
```
git clone https://github.com/lukasp2/cryptotaxsweden.git
```
2. Install requirements
```
pip install -r requirements.txt
```

## Usage - how to declare your crypto trades
1. Download transaction data as a CSV report from here:
```
https://www.coinbase.com/reports
```
2. Log in to cointracking and import the transaction data from here:
```
https://cointracking.info/import/coinbase/
```

3. Download cointracking transaction data as comma-separated CVS from here:
```
https://cointracking.info/trade_prices.php
```

4. Save transaction data under the `data/` folder as `trades.csv`

5. Enter your personal details in `data/personal_details.json`

6. Run the following from root of repo, assuming you want to report for year 2022:
```
python main.py 2022 --simplified-k4 --rounding-report --rounding-report-threshold=1 --format=sru
```

7. Check output for errors and make sure everything looks good

8. Test the generated .sru files (in the out folder) for errors here:
```
https://www1.skatteverket.se/fv/fv_web/filval.do
```

9. Submit blanketter.sru file to Skatteverket as a K4 attachment

## Understanding the Swedish crypto tax law
Here is an explaination of how the tax rules is applied to a series of purchases and sales of BTC.
1. Buy 10 BTC for 10'000 SEK.
2. Buy 10 BTC for 50'000 SEK. \
_On average, since you paid in total 60'000 SEK for 20 BTC, each BTC is now worth 3000 SEK to you ("omkostnadsbelopp"). This means:_ \
_Selling BTC for more than 3'000 SEK each will be regarded profit and is taxed._ \
_Selling BTC for less than 3'000 SEK each will be regarded as loss and is tax deductible._ \
_Buying BTC for more than 3'000 SEK each will do nothing except increase the omkostnadsbelopp._ \
_Buying BTC for less than 3'000 SEK each will do nothing except decrease the omkostnadsbelopp._ 

3. Sell 15 BTC for 60'000 SEK \
_15 BTC is worth 15 * 3'000 = 45'000 SEK to you, which means a profit of 15'000 SEK (60'000 - 45'000)._ \
_A sale does not affect omkostnadsbelopp -your remaining 5 BTC is still valued at 3000 SEK / each._

4. Buy 5 BTC for 25'000 SEK \
_You already had 5 * 3'000 SEK worth of BTC, now you have 10 BTC in total worth 40'000 SEK._ \
_Your 10 BTC is valued at 4'000 SEK each._

5. Sell 0.345 BTC for 2000 SEK \
_0.345 BTC is worth 0.345 * 4'000 = 1380 SEK to you, but you got 2000 SEK for it. Profit = 620 SEK._

6. Sell 5 BTC for 15'000 SEK \
_5 BTC is worth 5 * 4'000 = 20'000 SEK to you, which means a loss of 5'000 SEK._ \
_The loss is tax deductible by 70 %. 5'000 * 0.70 = 3500 SEK._

You can find the same example (but not as well explained) on Skatteverket website: \
https://skatteverket.se/privat/skatter/vardepapper/andratillgangar/kryptovalutor.4.15532c7b1442f256bae11b60.html

## Test
You can use `data/trades_test.csv` to test the script. The file contains the trades made in the example above.

1. validate that the trades in the file corresponds to the example
2. run 
```
python main.py 2021 --simplified-k4 --rounding-report --rounding-report-threshold=1 --format=sru --trades="data/trades_test.csv" --coin-report
```
3. check that profit, loss, and tax in the output under Section D is correct
4. check that `out/coin_report.csv` has the correct cost basis ("omkostnadsbelopp")

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
#### Generate a simplified report for 2021 in sru format.
```
python main.py 2021 --simplified-k4
```

#### Generate a simplified report for 2021 in sru format with a rounding report with threshold of 1%.
```
python main.py 2021 --simplified-k4 --rounding-report --rounding-report-threshold=1
```

#### Merging the generated pdf files
Merging the pdf files can be done with Ghostscript. It might make printing a bit easier.

```
cd out
gs -q -dNOPAUSE -dBATCH -sDEVICE=pdfwrite -sOutputFile=merged.pdf k4_no*.pdf
```

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
