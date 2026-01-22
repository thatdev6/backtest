# backtest/simulate.py

import pandas as pd
from engine.portfolio import buy_shares, portfolio_value
from engine.report import report_yearly_purchases_with_drift
from engine.logger import logger

def simulate_from_file(file_path, initial_capital):
    logger.info(f"Loading data from file: {file_path}")

    # -----------------------------
    # Load file
    # -----------------------------
    ext = file_path.split('.')[-1].lower()
    if ext == "csv":
        df_all = pd.read_csv(file_path)
    elif ext in ["xlsx", "xls"]:
        df_all = pd.read_excel(file_path)
    else:
        raise ValueError("File must be CSV or Excel")

    required_cols = ['ticker', 'date', 'weight']
    if not all(col in df_all.columns for col in required_cols):
        raise ValueError(f"File must contain columns: {required_cols}")

    df_all['date'] = pd.to_datetime(df_all['date'])
    df_all['year'] = df_all['date'].dt.year
    years = sorted(df_all['year'].unique())
    logger.info(f"Data contains {len(years)} years: {years}")

    capital = initial_capital
    history = []
    df_bought_year = {}
    capital_start_year = {}
    reports_by_year = {}

    # -----------------------------
    # Yearly simulation loop
    # -----------------------------
    for i, year in enumerate(years):
        logger.info(f"Processing year {year}")
        df_year = df_all[df_all['year'] == year].copy()
        capital_start_year[year] = capital

        # Buy shares at start of year
        df_bought = buy_shares(df_year[['ticker', 'date', 'weight']], capital).copy()

        # Drop rows with missing starting prices
        if df_bought['price'].isna().any():
            missing_tickers = df_bought[df_bought['price'].isna()]['ticker'].tolist()
            logger.warning(f"Dropping tickers with missing start prices: {missing_tickers}")
            df_bought = df_bought.dropna(subset=['price']).reset_index(drop=True)

        if df_bought.empty:
            raise RuntimeError(f"No valid assets to simulate in year {year} after removing missing prices.")

        # Re-normalize weights
        df_bought['weight'] = df_bought['weight'] / df_bought['weight'].sum()

        # Next-year tickers for rebalance logic
        next_year_tickers = set(df_all[df_all['year'] == years[i + 1]]['ticker']) if i < len(years) - 1 else set()

        # Generate yearly report
        report = report_yearly_purchases_with_drift(
            df_bought=df_bought,
            capital=capital,
            year=year,
            date_end=pd.to_datetime(f"{year + 1}-07-01"),
            next_year_tickers=next_year_tickers
        )
        reports_by_year[year] = report

        # Calculate end-of-year portfolio value
        total_value = portfolio_value(df_bought, pd.to_datetime(f"{year + 1}-07-01"))
        logger.info(f"End-of-year capital for {year}: {total_value:,.2f}")

        # Store cleaned portfolio and history
        df_bought_year[year] = df_bought.copy()
        history.append({
            'Year': year,
            'Capital Start': capital,
            'Capital End': total_value
        })
        capital = total_value

    history_df = pd.DataFrame(history)
    logger.info("Simulation completed.")
    logger.info(f"Final capital after {years[-1]}: {capital:,.2f}")

    return history_df, df_bought_year, capital_start_year, reports_by_year
