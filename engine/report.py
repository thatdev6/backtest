# backtest/engine/report.py
from engine.logger import info, warning
from engine.portfolio import get_price_on_or_after
import pandas as pd

def report_yearly_purchases_with_drift(
    df_bought,
    capital,
    year,
    date_end,
    next_year_tickers
):
    """
    Generates a yearly portfolio drift report:
    - Start-of-year values
    - 1Y weight drift
    - Rebalance action (Sold/Rebought + profit/loss)

    Returns:
        report: DataFrame of yearly report (without printing)
    """

    df = df_bought.copy().reset_index(drop=True)  # safe indexing

    # -----------------------------
    # Start-of-year values
    # -----------------------------
    df['value_start'] = df['shares'] * df['price']
    df['weight_start'] = df['value_start'] / capital

    # -----------------------------
    # End-of-year prices & values
    # -----------------------------
    df['price_end'] = df['ticker'].apply(lambda t: get_price_on_or_after(t, date_end))

    # Remove tickers with missing price
    missing_prices = df[df['price_end'].isna()]['ticker'].tolist()
    if missing_prices:
        warning(f"Removing tickers on {date_end.date()} due to missing price: {missing_prices}")
        df = df[df['price_end'].notna()].reset_index(drop=True)

    df['value_end'] = df['shares'] * df['price_end']
    total_end_value = df['value_end'].sum()
    df['weight_end'] = df['value_end'] / total_end_value if total_end_value > 0 else 0

    # -----------------------------
    # Weight drift
    # -----------------------------
    df['weight_change'] = df['weight_end'] - df['weight_start']

    # -----------------------------
    # Rebalance action logic
    # -----------------------------
    df['Action at Rebalance'] = df['ticker'].apply(
        lambda t: 'Rebought' if t in next_year_tickers else 'Sold'
    )

    df['Sold in Profit?'] = df.apply(
        lambda x:
            'Yes' if x['Action at Rebalance'] == 'Sold' and x['price_end'] > x['price']
            else 'No' if x['Action at Rebalance'] == 'Sold'
            else '—',
        axis=1
    )

    df['Sell Price (Rebalance)'] = df.apply(
        lambda x: x['price_end'] if x['Action at Rebalance'] == 'Sold' else None,
        axis=1
    )

    # -----------------------------
    # Final report table
    # -----------------------------
    report = df[[
        'ticker',
        'price',
        'shares',
        'weight_start',
        'price_end',
        'weight_end',
        'weight_change',
        'Action at Rebalance',
        'Sold in Profit?',
        'Sell Price (Rebalance)'
    ]].copy()

    report.columns = [
        'Ticker',
        'Buy Price',
        'Shares Bought',
        'Weight at Buy',
        'Price After 1Y',
        'Weight After 1Y',
        'Weight Change',
        'Action at Rebalance',
        'Sold in Profit?',
        'Sell Price (Rebalance)'
    ]

    info(f"Portfolio drift report prepared for year {year} — capital start: {capital:,.2f}, total end: {total_end_value:,.2f}")

    # Do NOT print here — main.py will handle CLI printing & CSV saving

    return report