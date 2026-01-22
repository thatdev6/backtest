# backtest/portfolio.py

import pandas as pd
import yfinance as yf
from datetime import timedelta
import logging
from engine.logger import logger  # import your configured logger

# -----------------------------
# Helper: Get price for a ticker on or after a date
# -----------------------------
def get_price_on_or_after(ticker, date):
    """
    Fetch the close price for a ticker on or after a given date.
    Returns float. Raises ValueError if no price found.
    """
    try:
        df = yf.download(
            ticker,
            start=date,
            end=pd.to_datetime(date) + timedelta(days=7),
            progress=False,
            auto_adjust=True
        )['Close']

        if df.empty:
            raise ValueError(f"No price data for {ticker} after {date}")

        if isinstance(df, pd.Series):
            return float(df.iloc[0])
        else:
            return float(df.iloc[0, 0])
    except Exception as e:
        logger.warning(f"Price fetch failed for {ticker} on {date}: {e}")
        raise

# -----------------------------
# Buy shares based on capital and weights
# -----------------------------
def buy_shares(df, capital):
    """
    Allocate capital to tickers based on weights and fetched prices.
    Rows where price cannot be fetched are removed.
    """
    df = df.copy()
    prices = []
    failed_rows = []

    for idx, row in df.iterrows():
        try:
            price = get_price_on_or_after(row['ticker'], row['date'])
            prices.append(price)
        except Exception:
            logger.warning(f"Removing {row['ticker']} on {row['date']} due to missing price")
            failed_rows.append(idx)
            prices.append(pd.NA)

    # Drop rows that failed
    if failed_rows:
        df.drop(index=failed_rows, inplace=True)
        df.reset_index(drop=True, inplace=True)
        prices = [p for i, p in enumerate(prices) if i not in failed_rows]

    df['price'] = prices
    df['allocation'] = df['weight'] * capital
    df['shares'] = df['allocation'] / df['price']

    logger.info(f"Bought shares for {len(df)} assets, {len(failed_rows)} removed due to missing prices")
    return df

# -----------------------------
# Compute portfolio value given shares and prices
# -----------------------------
def portfolio_value(df, date_end):
    """
    Compute total portfolio value at a specific date using fetched prices.
    """
    df = df.copy()
    prices = []
    failed_rows = []

    for idx, row in df.iterrows():
        try:
            price_end = get_price_on_or_after(row['ticker'], date_end)
            prices.append(price_end)
        except Exception:
            logger.warning(f"Removing {row['ticker']} on {date_end} due to missing price")
            failed_rows.append(idx)
            prices.append(pd.NA)

    if failed_rows:
        df.drop(index=failed_rows, inplace=True)
        df.reset_index(drop=True, inplace=True)
        prices = [p for i, p in enumerate(prices) if i not in failed_rows]

    df['price_end'] = prices
    total_value = (df['shares'] * df['price_end']).sum()
    logger.info(f"Portfolio value on {date_end}: {total_value:,.2f} ({len(df)} assets)")
    return total_value
