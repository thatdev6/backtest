# backtest

Assessment project for Plutus21 Capital.





\# Backtest Portfolio Simulation



\## \*\*Project Overview\*\*



This Python project simulates and analyzes portfolio performance based

on historical allocation data. It provides a structured backtesting

system that handles yearly portfolio rebalances, calculates key metrics,

and generates visualizations for performance analysis.



The backtest assumes \*\*assets are bought at the start of the year, held

for one year, and then sold/rebalanced according to the next year's

allocation data\*\*. No target weights are enforced beyond the given data.



------------------------------------------------------------------------



\## \*\*Folder Structure\*\*



``` text

backtest/

│

├── main.py                   # CLI script to run the backtest

├── data/                     # Initial portfolio input file

│   └── Assessment File.xlsx

├── Sessions/                 # Session-specific folders

│   └── <session\_name>/

│       ├── raw\_data/         # Copied original portfolio file

│       ├── processed\_data/   # Cleaned/preprocessed CSV

│       └── results/          # Yearly reports \& plots

├── logs/                     # Log files generated during runs

├── notebooks/                # Optional Jupyter notebooks for analysis

│

└── engine/

&nbsp;   ├── data\_loader.py        # File loading \& preprocessing

&nbsp;   ├── simulate.py           # Simulation engine

&nbsp;   ├── report.py             # Yearly drift reports

&nbsp;   ├── metrics.py            # Metrics calculations \& plots

&nbsp;   └── logger.py             # Logging utilities

```



------------------------------------------------------------------------



\## \*\*How to Run\*\*



1\.  Ensure Python 3.x is installed.

2\.  Install required packages from `requirements.txt`:



``` bash

pip install -r requirements.txt

```



3\.  Place your portfolio file in the `data/` folder.

4\.  Run the CLI:



``` bash

python main.py

```



5\.  Follow prompts:

&nbsp;   -   Enter session name

&nbsp;   -   Enter portfolio file path

&nbsp;   -   Specify column names for \*\*Ticker\*\*, \*\*Weight\*\*, and \*\*Date\*\*

&nbsp;   -   Enter \*\*initial capital\*\*

6\.  Check outputs in `Sessions/<session\_name>`:

&nbsp;   -   \*\*raw\_data/\*\* -- Original portfolio file

&nbsp;   -   \*\*processed\_data/\*\* -- Cleaned/preprocessed CSV

&nbsp;   -   \*\*results/\*\* -- Yearly reports \& plots



------------------------------------------------------------------------



\## \*\*Results Explanation\*\*



\### \*\*Yearly Reports\*\*



\*\*`report\_<year>.csv`\*\* contains, for each asset:



\-   \*\*Ticker\*\* -- Asset identifier\\

\-   \*\*Buy Price\*\* -- Price at start of year\\

\-   \*\*Shares Bought\*\* -- Number of shares purchased\\

\-   \*\*Weight at Buy\*\* -- Portfolio weight at purchase\\

\-   \*\*Price After 1Y\*\* -- Price at rebalance date\\

\-   \*\*Weight After 1Y\*\* -- Portfolio weight at end of year\\

\-   \*\*Weight Change\*\* -- Drift in portfolio allocation\\

\-   \*\*Action at Rebalance\*\* -- Sold / Rebought\\

\-   \*\*Sold in Profit?\*\* -- Yes / No\\

\-   \*\*Sell Price (Rebalance)\*\* -- Execution price



------------------------------------------------------------------------



\### \*\*Plots\*\*



For each year:



\-   \*\*Weight Change Bar Chart\*\* -- Portfolio drift visualization\\

\-   \*\*Price Change Bar Chart\*\* -- Asset-level price movements\\

\-   \*\*Portfolio Growth Line Chart\*\* -- Cumulative portfolio value



Plots are saved as `.png` files in `results/` and are \*\*not displayed in

the CLI\*\*.



------------------------------------------------------------------------



\### \*\*Metrics\*\*



\-   \*\*Yearly CAGR (%)\*\*

\-   \*\*Overall Portfolio Growth (%)\*\*

\-   \*\*Max Drawdown (%)\*\*

\-   \*\*Year of Max Drawdown\*\*

\-   \*\*Sharpe Ratio\*\*

\-   \*\*Total Profit\*\*



------------------------------------------------------------------------



\## \*\*Function Descriptions\*\*



\### \*\*engine/data\_loader.py\*\*



\-   `load\_file(file\_path)`

\-   `remove\_delisted\_tickers(df)`

\-   `preprocess\_file(file\_path, ticker\_col, weight\_col, date\_col)`

\-   `save\_clean\_csv(df, out\_path)`



------------------------------------------------------------------------



\### \*\*engine/simulate.py\*\*



\-   `simulate\_from\_file(file\_path, initial\_capital)`



------------------------------------------------------------------------



\### \*\*engine/report.py\*\*



\-   `report\_yearly\_purchases\_with\_drift(df\_bought, capital, year, date\_end, next\_year\_tickers)`



------------------------------------------------------------------------



\### \*\*engine/metrics.py\*\*



\-   `plot\_weight\_change\_bar(df\_report, year, out\_folder)`

\-   `plot\_price\_change\_bar(df\_report, year, out\_folder)`

\-   `plot\_portfolio\_growth(history\_df, out\_folder)`

\-   `run\_metrics(history\_df, session\_path, reports\_by\_year)`



------------------------------------------------------------------------



\## \*\*Formulas Used\*\*



\## \*\*Formulas Used\*\*



\### \*\*Weight at Buy\*\*



$$

\\text{Weight}\_{start} =

\\frac{\\text{Value of Shares Bought}}

{\\text{Total Portfolio Capital}}

$$



\### \*\*Weight After 1 Year\*\*



$$

\\text{Weight}\_{end} =

\\frac{\\text{Value at Rebalance}}

{\\text{Total Portfolio Value}}

$$



\### \*\*Weight Change\*\*



$$

\\Delta \\text{Weight} =

\\text{Weight}\_{end} - \\text{Weight}\_{start}

$$



\### \*\*Shares Bought\*\*



$$

\\text{Shares} =

\\frac{\\text{Weight} \\times \\text{Capital}}

{\\text{Price at Buy}}

$$



\### \*\*Value of Shares Bought\*\*



$$

\\text{Value} =

\\text{Shares} \\times \\text{Price at Buy}

$$



\### \*\*CAGR (Yearly)\*\*



$$

\\text{CAGR} =

\\left(

\\frac{\\text{Capital}\_{end}}

{\\text{Capital}\_{start}}

\\right)^{1} - 1

$$



\### \*\*Total Portfolio Growth\*\*



$$

\\text{Growth \\%} =

\\frac{\\text{Final Capital} - \\text{Initial Capital}}

{\\text{Initial Capital}}

\\times 100

$$



\### \*\*Drawdown\*\*



$$

\\text{Drawdown} =

\\frac{\\text{Peak Capital} - \\text{Capital}\_{end}}

{\\text{Peak Capital}}

$$



\### \*\*Sharpe Ratio\*\*



$$

\\text{Sharpe} =

\\frac{\\text{Mean Returns}}

{\\text{Standard Deviation of Returns}}

$$





------------------------------------------------------------------------



\## \*\*Assumptions\*\*



\-   Assets are bought at the start of the year

\-   Assets are held for one year

\-   Rebalancing occurs annually

\-   No optimization or target weighting

\-   Missing or delisted tickers are removed automatically



------------------------------------------------------------------------



\## \*\*Future Enhancements\*\*



\-   Monthly / intraday backtesting

\-   Additional risk metrics (Sortino, Beta, Volatility)

\-   Portfolio optimization

\-   GUI / web dashboard

\-   Dynamic rebalance strategies

\-   Automated data ingestion



------------------------------------------------------------------------



✅ \*\*End of README\*\*



