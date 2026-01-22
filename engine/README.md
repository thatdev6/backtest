
# Backtest Portfolio Simulation

Assessment project for Plutus21 Capital.

This Python project simulates and analyzes portfolio performance based on historical allocation data. It provides a structured backtesting system that handles yearly portfolio rebalances, calculates key metrics, and generates visualizations for performance analysis.




## File Structure

```text
backtest/
│
├── main.py                   # CLI script to run the backtest
├── data/                     # Initial portfolio input file
│   └── Assessment File.xlsx
├── Sessions/                 # Session-specific folders
│   └── <session_name>/
│       ├── raw_data/         # Copied original portfolio file
│       ├── processed_data/   # Cleaned/preprocessed CSV
│       └── results/          # Yearly reports & plots
├── logs/                     # Log files generated during runs
├── notebooks/                # Optional Jupyter notebooks for analysis
│
└── engine/
    ├── data_loader.py        # File loading & preprocessing
    ├── simulate.py           # Simulation engine
    ├── report.py             # Yearly drift reports
    ├── metrics.py            # Metrics calculations & plots
    └── logger.py             # Logging utilities
```

---
## How to Run

1. Ensure Python 3.x is installed.
2. Install required packages from `requirements.txt`:

```bash
pip install -r requirements.txt
```

3. Place your portfolio file in the `data/` folder.
4. Run the CLI:

```bash
python main.py
```
5. Follow prompts:
   - Enter session name
   - Enter portfolio file path
   - Specify column names for **Ticker**, **Weight**, and **Date**
   - Enter **initial capital**

6. Check outputs in `Sessions/<session_name>`:
   - `raw_data/` – Original portfolio file
   - `processed_data/` – Cleaned/preprocessed CSV
   - `results/` – Yearly reports and plots

---

## Results Explanation

### Yearly Reports

`report_<year>.csv` contains, for each asset:

- Ticker – Asset identifier
- Buy Price – Price at start of year
- Shares Bought – Number of shares purchased
- Weight at Buy – Portfolio weight at purchase
- Price After 1Y – Price at rebalance date
- Weight After 1Y – Portfolio weight at end of year
- Weight Change – Drift in portfolio allocation
- Action at Rebalance – Sold / Rebought
- Sold in Profit? – Yes / No
- Sell Price (Rebalance) – Execution price

---

### Plots

For each year:

- Weight Change Bar Chart – Portfolio drift visualization
- Price Change Bar Chart – Asset-level price movements
- Portfolio Growth Line Chart – Cumulative portfolio value

Plots are saved as `.png` files in `results/` and are **not displayed in the CLI**.

---

### Metrics

- Yearly CAGR (%)
- Overall Portfolio Growth (%)
- Max Drawdown (%)
- Year of Max Drawdown
- Sharpe Ratio
- Total Profit

---

## Function Descriptions

###  engine/data_loader.py

- `load_file(file_path)`  -   Load CSV/Excel and standardize columns

- `remove_delisted_tickers(df)` – Load CSV/Excel and standardize columns

- `preprocess_file(file_path, ticker_col, weight_col, date_col)` – Clean and normalize data

- `save_clean_csv(df, out_path)` – Clean and normalize data

### engine/simulate.py

- `simulate_from_file(file_path, initial_capital)` – Runs yearly backtest simulation and generates reports

### engine/report.py

- `report_yearly_purchases_with_drift(df_bought, capital, year, date_end, next_year_tickers)` – Creates yearly drift report table

### engine/metrics.py

- `plot_weight_change_bar(df_report, year, out_folder)` – Saves weight change bar chart

- `plot_price_change_bar(df_report, year, out_folder)` – Saves price change bar chart

- `plot_portfolio_growth(history_df, out_folder)` – Saves portfolio growth line chart

- `run_metrics(history_df, session_path, reports_by_year)` – Runs all metrics and saves plots

## Formulas Used

### Shares Bought

`(Weight × Capital) ÷ Price at Buy`

### Value of Shares Bought

`Shares Bought × Price at Buy`

### Weight at Buy 

`Value of Shares Bought ÷ Total Portfolio Capital`

### Weight After 1 Year

`Value at Rebalance ÷ Total Portfolio Value`

### Weight Change

`Weight After 1 Year − Weight at Buy`

### CAGR (Yearly)

`(Capital at End ÷ Capital at Start) − 1`

### Total Portfolio Growth

`(Final Capital − Initial Capital) ÷ Initial Capital × 100`

### Drawdown

`(Peak Capital − Capital at End) ÷ Peak Capital`

### Sharpe Ratio

`Mean Returns ÷ Standard Deviation of Returns`
## Assumptions

- Assets are bought at the start of the year and held for 1 year.

- At rebalance, all assets are sold and the next year’s assets are bought according to the given data.

- No target weights or optimization applied.

- Missing or delisted tickers are automatically removed.

- Portfolio is rebalanced once per year.


## Improvements that came to mind while working on it 

- Combine multiple yearly plots into single figures

- Include intraday or monthly backtesting

- Add additional risk metrics (Volatility, Sortino Ratio, Beta)

- Add portfolio optimization features

- Add GUI or web dashboard for visualization

- Improve logging and reporting customization

- Allow dynamic rebalance strategies

- Automate data fetching from multiple sources