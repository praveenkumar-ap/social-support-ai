# src/core/eligibility_engine.py

import os
import logging
from typing import List

# You may use joblib, pickle, etc. if you have a saved sklearn model.
# from sklearn.base import ClassifierMixin  

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class EligibilityEngine:
    """
    Wraps a trained ML model for eligibility prediction, with
    a rule-based fallback. All parameters are read from env vars.
    """
    def __init__(self):
        # 1) Load thresholds from environment, with defaults
        try:
            self.income_threshold = float(
                os.getenv("ELIGIBILITY_INCOME_THRESHOLD", "2000")
            )
            self.family_size_threshold = int(
                os.getenv("ELIGIBILITY_FAMILY_SIZE_THRESHOLD", "4")
            )
        except ValueError:
            logger.error("Invalid eligibility thresholds; using defaults")
            self.income_threshold = 2000.0
            self.family_size_threshold = 4

        # 2) Optionally load a trained model
        self.model = None
        model_path = os.getenv(
            "ELIGIBILITY_MODEL_PATH", "src/models/eligibility_model.pkl"
        )
        if os.path.isfile(model_path):
            try:
                import pickle
                with open(model_path, "rb") as f:
                    self.model = pickle.load(f)
                logger.info(f"Loaded eligibility model from '{model_path}'")
            except Exception:
                logger.exception(
                    f"Failed to load eligibility model at '{model_path}'; using rule-based"
                )

    def assess(self, income: float, family_size: int) -> str:
        """
        Return 'approved' or 'declined'.

        First attempts ML prediction;  
        if no model is available or prediction fails, uses rule:
        income * family_size < (income_threshold * family_size_threshold).
        """
        # Sanity‐check inputs
        if income < 0 or family_size < 1:
            logger.warning(
                "Received unexpected values: income=%r, family_size=%r",
                income, family_size,
            )

        # 1) ML path
        if self.model:
            try:
                features: List[List[float]] = [[income, float(family_size)]]
                pred = self.model.predict(features)[0]
                decision = "approved" if pred == 1 else "declined"
                logger.debug(
                    "ML model predicted %r for income=%.2f, family_size=%d",
                    decision, income, family_size,
                )
                return decision
            except Exception:
                logger.exception(
                    "Exception during ML predict; falling back to rule‐based"
                )

        # 2) Rule‐based fallback
        threshold = self.income_threshold * self.family_size_threshold
        score = income * family_size
        decision = "approved" if score < threshold else "declined"
        logger.info(
            "Rule-based decision=%r (income*family_size=%.2f, threshold=%.2f)",
            decision, score, threshold,
        )
        return decision