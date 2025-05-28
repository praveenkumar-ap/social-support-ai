#!/usr/bin/env python3
"""
Ingest credit reports from JSON or CSV files in a directory, consolidating into a single CSV.
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

def ingest_credit_reports(input_dir: str, output_csv: str):
    """
    Read all JSON and CSV credit report files in input_dir and concatenate into output_csv.

    :param input_dir: Directory containing credit report files (.json, .csv).
    :param output_csv: Path to save the consolidated CSV.
    """
    input_path = Path(input_dir)
    if not input_path.is_dir():
        logger.error(f"Input directory {input_dir} does not exist or is not a directory.")
        return

    files = list(input_path.glob("*.json")) + list(input_path.glob("*.csv"))
    if not files:
        logger.warning(f"No JSON or CSV files found in {input_dir}.")
        return

    dfs = []
    for file in files:
        try:
            logger.info(f"Reading credit report file: {file}")
            if file.suffix.lower() == ".json":
                df = pd.read_json(file, lines=True)
            else:
                df = pd.read_csv(file)
            # Standardize columns if necessary
            # e.g., df = df.rename(columns={'credit_score': 'score'})
            dfs.append(df)
        except ValueError as ve:
            logger.exception(f"Failed to parse {file}: {ve}")
        except Exception as e:
            logger.exception(f"Failed to read {file}: {e}")

    if not dfs:
        logger.error("No valid credit report files were processed.")
        return

    try:
        combined = pd.concat(dfs, ignore_index=True, sort=False)
        os.makedirs(Path(output_csv).parent, exist_ok=True)
        combined.to_csv(output_csv, index=False)
        logger.info(f"Consolidated credit reports saved to {output_csv}")
    except Exception as e:
        logger.exception(f"Failed to write consolidated CSV: {e}")

def main():
    parser = argparse.ArgumentParser(description="Ingest credit report files into a single CSV")
    parser.add_argument(
        "--input-dir",
        type=str,
        default=os.getenv("CREDIT_REPORTS_DIR", "data/raw/credit_reports"),
        help="Directory containing credit report files"
    )
    parser.add_argument(
        "--output-csv",
        type=str,
        default=os.getenv("CREDIT_REPORTS_OUTPUT", "data/processed/credit_reports.csv"),
        help="Path to save the consolidated CSV"
    )
    args = parser.parse_args()

    ingest_credit_reports(args.input_dir, args.output_csv)

if __name__ == "__main__":
    main()
