"""
Training script for Eligibility and Recommendation models.
"""

import os
import logging
import argparse
import pickle

import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report

from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger(__name__)

def train_eligibility_model(
    input_csv: str,
    model_output_path: str,
    test_size: float = 0.2,
    random_state: int = 42
):
    """
    Train a logistic regression model for eligibility.
    Expects a CSV with columns: income, family_size, doc_count, label
    where label is 1 (approve) or 0 (soft decline).
    """
    logger.info(f"Loading training data from {input_csv}")
    df = pd.read_csv(input_csv)
    if not {'income', 'family_size', 'doc_count', 'label'}.issubset(df.columns):
        logger.error("Input CSV missing required columns")
        return

    X = df[['income', 'family_size', 'doc_count']]
    y = df['label']

    logger.info("Splitting data")
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=random_state
    )

    logger.info("Training LogisticRegression model")
    model = LogisticRegression(max_iter=1000)
    model.fit(X_train, y_train)

    logger.info("Evaluating model")
    preds = model.predict(X_test)
    report = classification_report(y_test, preds)
    logger.info(f"Classification report:\n{report}")

    # Save model
    os.makedirs(os.path.dirname(model_output_path), exist_ok=True)
    with open(model_output_path, 'wb') as f:
        pickle.dump(model, f)
    logger.info(f"Model saved to {model_output_path}")

def main():
    load_dotenv()
    parser = argparse.ArgumentParser(description="Train eligibility model")
    parser.add_argument(
        "--input-csv",
        type=str,
        default=os.getenv("ELIGIBILITY_TRAINING_CSV", "data/processed/eligibility_training.csv"),
        help="Path to training CSV"
    )
    parser.add_argument(
        "--output-model",
        type=str,
        default=os.getenv("ELIGIBILITY_MODEL_PATH", "src/models/eligibility_model.pkl"),
        help="Path to save trained model"
    )
    args = parser.parse_args()

    try:
        train_eligibility_model(
            input_csv=args.input_csv,
            model_output_path=args.output_model
        )
    except Exception:
        logger.exception("Failed to train eligibility model")

if __name__ == "__main__":
    main()