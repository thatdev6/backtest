# backtest/engine/data_loader.py

import pandas as pd
import os
import yfinance as yf
from .logger import info, warning, error

# -----------------------------
# File Loader
# -----------------------------
def load_file(file_path: str) -> pd.DataFrame:
    if not os.path.exists(file_path):
        error(f"File not found: {file_path}")
        raise FileNotFoundError(f"File not found: {file_path}")

    ext = os.path.splitext(file_path)[1].lower()

    # ---------------- CSV ----------------
    if ext == ".csv":
        df = pd.read_csv(file_path)

    # ---------------- Excel ----------------
    elif ext in [".xlsx", ".xls"]:
        df = pd.read_excel(file_path, header=None)

        # Case 1: Proper multi-column Excel
        if df.shape[1] > 1:
            df.columns = df.iloc[0].astype(str).str.strip()
            df = df.iloc[1:].reset_index(drop=True)

        # Case 2: Single-column, comma-separated
        else:
            split_df = (
                df.iloc[:, 0]
                .astype(str)
                .str.strip()
                .str.split(",", expand=True)
            )

            if split_df.shape[1] < 3:
                error("Malformed file: cannot infer structure.")
                raise ValueError("Malformed file: cannot infer structure.")

            split_df.columns = split_df.iloc[0].astype(str).str.strip()
            df = split_df.iloc[1:].reset_index(drop=True)

    else:
        error(f"Unsupported file format: {ext}")
        raise ValueError(f"Unsupported file format: {ext}")

    # Clean column names aggressively
    df.columns = df.columns.astype(str).str.strip().str.replace("\ufeff", "", regex=False)
    info(f"File loaded successfully: {file_path} ({len(df)} rows)")
    return df


# -----------------------------
# Delisted Ticker Filter
# -----------------------------
def remove_delisted_tickers(df: pd.DataFrame) -> pd.DataFrame:
    """
    Removes tickers that cannot fetch any historical data from Yahoo Finance.
    """
    valid_tickers = []

    for t in df['ticker'].unique():
        try:
            ticker_obj = yf.Ticker(t)
            hist = ticker_obj.history(period="1d")
            # Must have at least one row to be valid
            if hist.empty:
                warning(f"Ticker removed (delisted or no data): {t}")
            else:
                valid_tickers.append(t)
        except Exception as e:
            warning(f"Ticker removed (fetch error): {t} ({e})")

    # Filter original dataframe
    df_filtered = df[df['ticker'].isin(valid_tickers)].reset_index(drop=True)
    info(f"Delisted tickers removed. {len(df_filtered)} valid rows remain.")
    return df_filtered

# -----------------------------
# Preprocessing
# -----------------------------
def preprocess_file(
    file_path: str,
    ticker_col: str,
    weight_col: str,
    date_col: str,
    skip_delisted_check: bool = False
) -> pd.DataFrame:
    df = load_file(file_path)

    # Validate required columns
    missing = [c for c in [ticker_col, weight_col, date_col] if c not in df.columns]
    if missing:
        error(f"Missing required columns: {missing}")
        raise ValueError(f"Missing required columns: {missing}")

    # Standardize column names
    df = df.rename(columns={
        ticker_col: "ticker",
        weight_col: "weight",
        date_col: "date"
    })

    # Type conversions
    df["date"] = pd.to_datetime(df["date"], errors="raise")
    df["weight"] = pd.to_numeric(df["weight"], errors="raise")

    # Remove delisted tickers before further processing
    if not skip_delisted_check:
        df = remove_delisted_tickers(df)

    # Normalize weights per date
    df["weight"] = df["weight"] / df.groupby("date")["weight"].transform("sum")

    # Sort
    df = df.sort_values(["date", "ticker"]).reset_index(drop=True)

    info(f"Data preprocessed successfully ({len(df)} rows)")
    return df


# -----------------------------
# Save Clean CSV
# -----------------------------
def save_clean_csv(df: pd.DataFrame, out_path="data/df_clean.csv") -> str:
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    df.to_csv(out_path, index=False)
    info(f"Clean data saved to: {out_path}")
    return os.path.abspath(out_path)
