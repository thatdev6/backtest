# backtest/engine/metrics.py

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from engine.logger import logger
import os

# -----------------------------
# Portfolio Weight Change Bar
# -----------------------------
def plot_weight_change_bar(df_report, year, out_folder):
    df = df_report.copy().sort_values('Weight Change')
    color_map = {'Rebought': 'green', 'Sold': 'red'}
    colors = df['Action at Rebalance'].map(color_map).fillna('gray')

    plt.figure(figsize=(10,6))
    bars = plt.bar(df['Ticker'], df['Weight Change'], color=colors, edgecolor='black', alpha=0.8)
    plt.axhline(0, color='black', linestyle='--')
    plt.xlabel("Asset")
    plt.ylabel("Weight Change (After 1Y − At Buy)")
    plt.title(f"Portfolio Weight Drift — Year {year}")
    plt.xticks(rotation=45, ha='right')
    plt.legend(handles=[Patch(facecolor='green', edgecolor='black', label='Rebought'),
                        Patch(facecolor='red', edgecolor='black', label='Sold'),
                        Patch(facecolor='gray', edgecolor='black', label='No Rebalance')])

    for bar in bars:
        h = bar.get_height()
        if abs(h) > 0.005:
            plt.text(bar.get_x() + bar.get_width()/2, h,
                     f"{h:+.3f}", ha='center',
                     va='bottom' if h>0 else 'top', fontsize=9)

    plt.tight_layout()
    file_path = os.path.join(out_folder, f"weight_change_{year}.png")
    plt.savefig(file_path)
    plt.close()
    logger.info(f"Weight change bar saved: {file_path}")
    return file_path


# -----------------------------
# Asset Price Change Bar
# -----------------------------
def plot_price_change_bar(df_report, year, out_folder):
    df = df_report.copy()
    df['Price Change'] = df['Price After 1Y'] - df['Buy Price']
    df = df.sort_values('Price Change')
    color_map = {'Rebought': 'green', 'Sold': 'red'}
    colors = df['Action at Rebalance'].map(color_map).fillna('gray')

    plt.figure(figsize=(12,6))
    plt.bar(df['Ticker'], df['Price Change'], color=colors, edgecolor='black', alpha=0.8)
    plt.axhline(0, color='black', linestyle='--')
    plt.xlabel("Asset")
    plt.ylabel("Price Change (After 1Y − Buy)")
    plt.title(f"Asset Price Change — Year {year}")
    plt.xticks(rotation=45, ha='right')
    plt.legend(handles=[Patch(facecolor='green', edgecolor='black', label='Rebought'),
                        Patch(facecolor='red', edgecolor='black', label='Sold'),
                        Patch(facecolor='gray', edgecolor='black', label='No Rebalance')])
    plt.tight_layout()
    file_path = os.path.join(out_folder, f"price_change_{year}.png")
    plt.savefig(file_path)
    plt.close()
    logger.info(f"Price change bar saved: {file_path}")
    return file_path


# -----------------------------
# Portfolio Growth Line
# -----------------------------
def plot_portfolio_growth(history_df, out_folder):
    df = history_df.copy()
    plt.figure(figsize=(10,6))
    plt.plot(df['Year'], df['Capital End'], marker='o', linestyle='-', color='blue', linewidth=2)

    for i, row in df.iterrows():
        plt.text(row['Year'], row['Capital End'], f"{row['Capital End']:,.0f}", ha='center', va='bottom', fontsize=9)

    plt.xlabel("Year")
    plt.ylabel("Portfolio Value")
    plt.title("Portfolio Growth Over Time")
    plt.grid(True, linestyle='--', alpha=0.5)
    plt.xticks(df['Year'])
    plt.tight_layout()
    file_path = os.path.join(out_folder, "portfolio_growth.png")
    plt.savefig(file_path)
    plt.close()
    logger.info(f"Portfolio growth line saved: {file_path}")
    return file_path


# -----------------------------
# Run all metrics for the session
# -----------------------------
def run_metrics(history_df, session_path, reports_by_year=None):
    results_folder = os.path.join(session_path, "results")
    os.makedirs(results_folder, exist_ok=True)

    # -----------------------------
    # Compute metrics
    yearly_cagr = {}
    for idx, row in history_df.iterrows():
        start = row['Capital Start']
        end = row['Capital End']
        cagr = ((end / start) ** (1/1) - 1) * 100
        yearly_cagr[int(row['Year'])] = round(float(cagr), 2)

    overall_growth = round(float((history_df['Capital End'].iloc[-1] / 
                                  history_df['Capital Start'].iloc[0] - 1) * 100), 2)

    total_profit = round(float(history_df['Capital End'].iloc[-1] - 
                               history_df['Capital Start'].iloc[0]), 2)

    capital_series = history_df['Capital End'].cummax()
    drawdowns = (capital_series - history_df['Capital End']) / capital_series
    max_drawdown = round(float(drawdowns.max() * 100), 2)
    year_max_drawdown = int(history_df.loc[drawdowns.idxmax(), 'Year'])

    returns = history_df['Capital End'].pct_change().dropna()
    sharpe_ratio = round(float((returns.mean() / returns.std()) * np.sqrt(1)), 2) if len(returns) > 1 else float('nan')

    # -----------------------------
    # Save yearly plots
    saved_files = []
    if reports_by_year:
        for year, report in reports_by_year.items():
            f1 = plot_weight_change_bar(report, year, results_folder)
            f2 = plot_price_change_bar(report, year, results_folder)
            saved_files.extend([f1,f2])

    # Portfolio growth
    f3 = plot_portfolio_growth(history_df, results_folder)
    saved_files.append(f3)

    # -----------------------------
    # Return metrics dict (no printing, just saved files)
    metrics = {
        'Yearly CAGR %': yearly_cagr,
        'Overall Portfolio Growth %': overall_growth,
        'Max Drawdown %': max_drawdown,
        'Year of Max Drawdown': year_max_drawdown,
        'Sharpe Ratio': sharpe_ratio,
        'Total Profit': total_profit,
        'saved_files': saved_files
    }

    logger.info(f"All metrics plots saved in {results_folder}")
    return metrics
