#!/usr/bin/env python3
"""
Ingest bank statements from CSV files in a directory, consolidating into a single CSV.
"""

import os
import argparse
import logging
from pathlib import Path

import pandas as pd

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger(__name__)

def ingest_statements(input_dir: str, output_csv: str):
    """
    Read all CSV bank statements in input_dir and concatenate into output_csv.

    :param input_dir: Directory containing bank statement CSV files.
    :param output_csv: Path to save the consolidated CSV.
    """
    input_path = Path(input_dir)
    if not input_path.is_dir():
        logger.error(f"Input directory {input_dir} does not exist or is not a directory.")
        return

    all_files = list(input_path.glob("*.csv"))
    if not all_files:
        logger.warning(f"No CSV files found in {input_dir}.")
        return

    dfs = []
    for file in all_files:
        try:
            logger.info(f"Reading CSV file: {file}")
            df = pd.read_csv(file)
            # Optionally, perform standardization or column renaming here:
            # df = df.rename(columns={'Txn Date': 'date', 'Amount': 'amount', ...})
            dfs.append(df)
        except Exception as e:
            logger.exception(f"Failed to read {file}: {e}")

    if not dfs:
        logger.error("No valid CSV files were processed.")
        return

    try:
        combined = pd.concat(dfs, ignore_index=True)
        os.makedirs(Path(output_csv).parent, exist_ok=True)
        combined.to_csv(output_csv, index=False)
        logger.info(f"Consolidated bank statements saved to {output_csv}")
    except Exception as e:
        logger.exception(f"Failed to write consolidated CSV: {e}")

def main():
    parser = argparse.ArgumentParser(description="Ingest bank statement CSVs into a single file")
    parser.add_argument(
        "--input-dir",
        type=str,
        default=os.getenv("BANK_STATEMENTS_DIR", "data/raw/bank_statements"),
        help="Directory containing bank statement CSV files"
    )
    parser.add_argument(
        "--output-csv",
        type=str,
        default=os.getenv("BANK_STATEMENTS_OUTPUT", "data/processed/bank_statements.csv"),
        help="Path to save the consolidated CSV"
    )
    args = parser.parse_args()

    ingest_statements(args.input_dir, args.output_csv)

if __name__ == "__main__":
    main()
