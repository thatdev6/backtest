# backtest/main.py

import os
import shutil
import numpy as np
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from engine.logger import info, warning, error, setup_logger
from engine.data_loader import preprocess_file, save_clean_csv
from engine.simulate import simulate_from_file
from engine.metrics import run_metrics

console = Console()
logger = setup_logger()


# -----------------------------
# Session Management
# -----------------------------
def create_session_folder(base_dir="Sessions"):
    os.makedirs(base_dir, exist_ok=True)

    while True:
        session_name = input("Enter session name: ").strip()
        if not session_name:
            warning("Session name cannot be empty.")
            continue

        session_path = os.path.join(base_dir, session_name)
        if os.path.exists(session_path):
            warning("Session folder already exists. Please choose a different name.")
        else:
            os.makedirs(session_path)
            os.makedirs(os.path.join(session_path, "raw_data"))
            os.makedirs(os.path.join(session_path, "processed_data"))
            os.makedirs(os.path.join(session_path, "results"))
            info(f"Session created: {session_path}")
            return session_path


# -----------------------------
# Main Function
# -----------------------------
def main():
    info("Starting Backtest CLI")

    # Session folder setup
    session_path = create_session_folder()

    # Ask for portfolio file
    file_path = input("Enter path to portfolio file (CSV/XLSX): ").strip()
    if not os.path.exists(file_path):
        error(f"File not found: {file_path}")
        return

    # Copy raw file to session/raw_data
    raw_data_path = os.path.join(session_path, "raw_data", os.path.basename(file_path))
    shutil.copy(file_path, raw_data_path)
    info(f"Raw data copied to session: {raw_data_path}")

    # Ask for columns
    ticker_col = input("Enter the column name for Ticker/Identifier: ").strip()
    weight_col = input("Enter the column name for Weight: ").strip()
    date_col = input("Enter the column name for Date: ").strip()

    # Preprocess
    try:
        df_clean = preprocess_file(
            file_path=raw_data_path,
            ticker_col=ticker_col,
            weight_col=weight_col,
            date_col=date_col
        )
        # Save cleaned CSV
        processed_path = os.path.join(session_path, "processed_data", "df_clean.csv")
        save_clean_csv(df_clean, processed_path)
        info(f"Data loaded and cleaned ({len(df_clean)} rows).")
    except Exception as e:
        error(f"Failed to load or preprocess file: {e}")
        return

    # Initial capital
    while True:
        try:
            initial_capital = float(input("Enter initial capital (e.g., 100000): ").strip())
            break
        except ValueError:
            warning("Invalid input. Please enter a numeric value.")

    # Run simulation
    try:
        history_df, df_bought_year, capital_start_year, reports_by_year = simulate_from_file(
            file_path=processed_path,
            initial_capital=initial_capital
        )
        info("Simulation complete!")

        # -----------------------------
        # Print yearly portfolio drift reports
        from rich import box

        for year, report in reports_by_year.items():
            table = Table(
                title=f"Portfolio Drift Report — Year {year}",
                show_lines=True,
                box=box.SIMPLE_HEAVY
            )
            for col in report.columns:
                table.add_column(col, justify="right" if np.issubdtype(report[col].dtype, np.number) else "left")
            for _, row in report.iterrows():
                table.add_row(*[f"{v:,.2f}" if isinstance(v, (float,int)) else str(v) for v in row])
            console.print(table)

            # Save report CSV
            report.to_csv(os.path.join(session_path, "results", f"report_{year}.csv"), index=False)

    except Exception as e:
        error(f"Simulation failed: {e}")
        return

    # -----------------------------
    # Run metrics (plots saved silently)
    try:
        metrics_dict = run_metrics(history_df, session_path, reports_by_year)

        # Optional: print summary metrics in CLI
        console.print(Panel.fit("[bold green]Metrics Summary[/bold green]"))
        for key, value in metrics_dict.items():
            if key == "saved_files":
                continue  # skip printing file paths
            console.print(f"[cyan]{key}:[/cyan] {value}")

        info("Metrics calculated and all plots saved in results folder.")

    except Exception as e:
        error(f"Metrics calculation failed: {e}")
        return

    info("Backtest finished successfully!")


if __name__ == "__main__":
    main()
