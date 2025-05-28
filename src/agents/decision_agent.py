"""
DecisionAgent: combines eligibility and recommendation to produce a final decision.
"""

import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

class DecisionAgent:
    def __init__(self):
        """
        Initialize the decision agent.
        """
        pass

    def decide(
        self,
        eligibility: str,
        recommendation: str,
        processed_data: Dict[str, Any]
    ) -> str:
        """
        Produce a final decision based on eligibility and recommendation.
        
        :param eligibility: result from EligibilityEngine ("Approve" or "Soft Decline")
        :param recommendation: text from RecommendationEngine
        :param processed_data: data from DocumentProcessor (for potential future use)
        :return: combined decision string
        """
        try:
            logger.info("DecisionAgent: starting final decision assembly")
            
            if eligibility == "Approve":
                decision = (
                    f"✅ APPROVED: Your application meets our criteria. {recommendation}"
                )
            else:
                decision = (
                    f"⚠️ SOFT DECLINE: Your application did not meet all criteria. "
                    f"{recommendation}"
                )
            
            logger.info(f"DecisionAgent: final decision => {decision}")
            return decision
        except Exception:
            logger.exception("DecisionAgent: error assembling final decision")
            # On unexpected error, return a safe fallback
            return "⚠️ Error determining final decision; please try again later."