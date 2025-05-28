#!/usr/bin/env python3
"""
Train a simple eligibility classifier and serialize it to disk.

Reads a CSV with columns:
  - income (float)
  - family_size (int)
  - eligible (0 or 1)

Writes:
  - a scikit-learn model at ELIGIBILITY_MODEL_PATH
"""

import os
import sys
import logging
import argparse

import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
import joblib


# ────────────────────────────────────────────────────────────────────────────────
# Logging Setup
# ────────────────────────────────────────────────────────────────────────────────
logger = logging.getLogger("train_eligibility_model")
logger.setLevel(logging.INFO)
handler = logging.StreamHandler(sys.stdout)
formatter = logging.Formatter(
    "%(asctime)s %(levelname)s [%(name)s] %(message)s", "%Y-%m-%d %H:%M:%S"
)
handler.setFormatter(formatter)
logger.addHandler(handler)


def parse_args():
    parser = argparse.ArgumentParser(
        description="Train eligibility model and save to disk"
    )
    parser.add_argument(
        "--csv-path",
        default=os.getenv("ELIGIBILITY_TRAINING_CSV", "data/processed/eligibility_training.csv"),
        help="Path to training CSV (income,family_size,eligible)",
    )
    parser.add_argument(
        "--model-path",
        default=os.getenv("ELIGIBILITY_MODEL_PATH", "src/models/eligibility_model.pkl"),
        help="Where to save the trained model",
    )
    parser.add_argument(
        "--test-size",
        type=float,
        default=0.2,
        help="Proportion of data to reserve for testing",
    )
    parser.add_argument(
        "--random-state",
        type=int,
        default=42,
        help="Random seed for train/test split",
    )
    return parser.parse_args()


def main():
    args = parse_args()

    # 1) Load CSV
    logger.info("Loading data from %r", args.csv_path)
    if not os.path.isfile(args.csv_path):
        logger.error("Training CSV not found: %r", args.csv_path)
        sys.exit(1)

    try:
        df = pd.read_csv(args.csv_path)
    except Exception as e:
        logger.exception("Failed to read CSV")
        sys.exit(1)

    required_cols = {"income", "family_size", "eligible"}
    if not required_cols.issubset(df.columns):
        logger.error(
            "CSV missing required columns: %s (got %s)",
            required_cols, df.columns.tolist()
        )
        sys.exit(1)

    # 2) Prepare features and labels
    X = df[["income", "family_size"]].astype(float)
    y = df["eligible"].astype(int)

    # 3) Split
    logger.info("Splitting data: test_size=%.2f, random_state=%d",
                args.test_size, args.random_state)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=args.test_size, random_state=args.random_state
    )

    # 4) Train
    logger.info("Training LogisticRegression model")
    model = LogisticRegression(max_iter=1000)
    try:
        model.fit(X_train, y_train)
    except Exception:
        logger.exception("Model training failed")
        sys.exit(1)

    # 5) Evaluate
    logger.info("Evaluating on test set")
    preds = model.predict(X_test)
    report = classification_report(y_test, preds, target_names=["declined","approved"])
    logger.info("\n%s", report)

    # 6) Serialize
    os.makedirs(os.path.dirname(args.model_path), exist_ok=True)
    try:
        joblib.dump(model, args.model_path)
        logger.info("Model saved to %r", args.model_path)
    except Exception:
        logger.exception("Failed to save model to disk")
        sys.exit(1)


if __name__ == "__main__":
    main()