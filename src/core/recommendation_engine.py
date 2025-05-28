"""
RecommendationEngine: generates enablement recommendations based on processed applicant data.
"""

import os
import logging
from typing import Any, Dict
import pandas as pd
import io
import re

from dotenv import load_dotenv

logger = logging.getLogger(__name__)
load_dotenv()

class RecommendationEngine:
    def __init__(self):
        """
        Initialize the recommendation engine.
        Loads environment-based thresholds.
        """
        try:
            self.doc_threshold = int(os.getenv("RECOMMEND_DOC_THRESHOLD", 2))
            self.low_income_threshold = float(os.getenv("LOW_INCOME_THRESHOLD", 500))
            self.high_family_size_threshold = int(os.getenv("HIGH_FAMILY_SIZE_THRESHOLD", 6))
        except ValueError as e:
            logger.error(f"Invalid threshold configuration; using defaults: {e}")
            self.doc_threshold = 2
            self.low_income_threshold = 500
            self.high_family_size_threshold = 6

    def generate(self, processed_data: Dict) -> str:
        """
        Generate a recommendation based on rule-based logic.

        :param processed_data: dict from AgentOrchestrator
        :return: recommendation text
        """
        return self._rule_based(processed_data)

    def _rule_based(self, processed_data: Dict) -> str:
        income = processed_data.get("eligibility_inputs", {}).get("income", 0)
        family_size = processed_data.get("eligibility_inputs", {}).get("family_size", 0)
        doc_count = len(processed_data.get("documents", []))
        ocr_texts = processed_data.get("ocr_texts", [])
        employment_count = processed_data.get("resume_data", {}).get("employment_count", 0)
        net_worth = processed_data.get("financial_data", {}).get("net_worth", 0)
    


        total_ocr_length = sum(len(text) for text in ocr_texts)

        eligibility = processed_data.get("eligibility", "unknown")

        logger.info(
            f"Rule-based recommendation inputs: income={income}, "
            f"family_size={family_size}, doc_count={doc_count}, "
            f"ocr_text_length={total_ocr_length}, eligibility={eligibility}"
        )

        # Priority rules (order matters):

        # Rule 1: Already eligible (approved applicants)
        if eligibility == "approved":
            if income < self.low_income_threshold:
                return (
                    "Congratulations on approval! Given your current financial situation, "
                    "we strongly recommend exploring immediate financial support options "
                    "and basic aid programs in addition to career counseling."
                )
            elif family_size >= self.high_family_size_threshold:
                return (
                    "You're approved! Given your larger family size, we recommend "
                    "family-focused financial planning, career counseling, and job matching services."
                )
            else:
                return (
                    "Congratulations! Since you’re eligible, we recommend exploring "
                    "upskilling programs, career counseling, and job matching services."
                )
    

        # Rule 2: Low income applicants not yet approved
        if income < self.low_income_threshold:
            return (
                "Your income indicates you might be eligible for basic financial assistance. "
                "Please provide additional supporting documents such as income statements or "
                "bank statements for further evaluation."
            )

        # Rule 3: Large family size, not yet approved
        if family_size >= self.high_family_size_threshold:
            return (
                "Given your family size, you may qualify for family-oriented financial support. "
                "We suggest submitting additional documents like identification and "
                "proof of family members for further assessment."
            )

        # Rule 4: Many documents provided (engaged applicant)
        if doc_count >= self.doc_threshold:
            return (
                "Thank you for providing extensive documentation. We recommend exploring "
                "various upskilling programs, career counseling, and tailored job matching services."
            )

        # Rule 5: Detailed OCR texts indicate thorough documentation
        if total_ocr_length > 1000:
            return (
                "Your detailed documents suggest a proactive approach. "
                "We encourage you to consider advanced career development "
                "and professional training opportunities."
            )
        
        if processed_data.get("eligibility") == "approved":
            return (
                "Congratulations! Since you’re eligible, we recommend you explore "
                "upskilling programs, career counseling, and job matching services."
            )
        
        if income < 500:
            return (
                "We see your income is low. You may qualify for basic financial aid programs; "
                "please visit your nearest support center."
            )
        
        if employment_count == 0:
            return (
                "Your resume lacks clear employment history. "
                "Consider entry-level training and career counseling."
            )
        
         # NEW: Financial position rule
        if net_worth < 0:
            return (
                "Your financial data indicates significant liabilities. "
                "We recommend financial counseling and debt management programs."
           )

        if doc_count >= self.doc_threshold:
           return (
                "Based on your documents, we recommend upskilling programs, career counseling, "
                "and job matching services."
           )


        # Fallback: minimal information provided
        return (
            "To better assist you, please provide additional supporting documents "
            "(e.g., bank statements, identification, or credit reports) "
            "so we can offer more precise recommendations."
        )

    def parse_resume(self, ocr_text: str) -> Dict[str, Any]:
        """
        Basic structured parsing of resume text.
        Extract simple employment history: job titles and duration.
        """
        employment_history = []
        pattern = re.compile(r"(?:Title|Position|Role):\s*(.+)\s*(?:Duration|Period):\s*(.+)", re.I)
        matches = pattern.findall(ocr_text)

        for title, duration in matches:
            employment_history.append({"title": title.strip(), "duration": duration.strip()})

        return {
            "employment_history": employment_history,
            "employment_count": len(employment_history)
        }
    

    def parse_financial_csv(self, csv_content: bytes) -> Dict[str, Any]:
        """
        Simple structured parsing for assets/liabilities CSV.
        """
        try:
            df = pd.read_csv(io.BytesIO(csv_content))
            total_assets = df.get("Assets", pd.Series([0])).sum()
            total_liabilities = df.get("Liabilities", pd.Series([0])).sum()
            net_worth = total_assets - total_liabilities
        except Exception as e:
            logger.error(f"CSV parsing failed: {e}")
            total_assets = total_liabilities = net_worth = 0.0

        return {
            "total_assets": total_assets,
            "total_liabilities": total_liabilities,
            "net_worth": net_worth
        }