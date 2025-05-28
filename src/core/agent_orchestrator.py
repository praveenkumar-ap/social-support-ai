import logging
from typing import List, Dict, Any

from src.core.image_ocr import ImageOCR
from src.core.eligibility_engine import EligibilityEngine
from src.core.recommendation_engine import RecommendationEngine

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

class AgentOrchestrator:
    """
    Orchestrates:
      1) OCR on images (skipping non-images)
      2) Eligibility check
      3) Recommendation
      4) Final decision
    """

    def __init__(self):
        self.ocr = ImageOCR()
        self.eligibility_engine = EligibilityEngine()
        self.recommendation_engine = RecommendationEngine()

    def run(
        self,
        applicant_id: str,
        documents: List[str],
        income: float,
        family_size: int
    ) -> Dict[str, Any]:
        processed_data: Dict[str, Any] = {}
        processed_data["documents"] = documents

        # 1) OCR (skip non-images)
        try:
            ocr_texts = self.ocr.extract_texts(documents)
            processed_data["ocr_texts"] = ocr_texts
        except Exception as e:
            logger.exception("❌ OCR processing failed; continuing without OCR")
            processed_data["ocr_texts"] = []
            resume_data = {}
            financial_data = {}
            
            for doc, text in zip(documents, text):
                if "resume" in doc.lower():
                     resume_data = self.doc_processor.parse_resume(text)
                elif doc.lower().endswith(('.csv', '.xls', '.xlsx')):
                    with open(doc, 'rb') as f:
                        financial_data = self.doc_processor.parse_financial_csv(f.read())

            processed_data["resume_data"] = resume_data
            processed_data["financial_data"] = financial_data
        
        except Exception as e:
            logger.exception("❌ OCR and structured parsing step encountered an issue for applicant %r", applicant_id)
            raise RuntimeError("OCR or parsing failed") from e


        # 2) Eligibility
        try:
            eligibility = self.eligibility_engine.assess(
                income=income,
                family_size=family_size
            )
            processed_data["eligibility_inputs"] = {
                "income": income,
                "family_size": family_size
            }
            processed_data["eligibility"] = eligibility
            logger.info(
                "Eligibility for %r: income=%.2f, family_size=%d → %s",
                applicant_id, income, family_size, eligibility
            )
        except Exception:
            logger.exception("❌ Eligibility assessment failed; defaulting to 'declined'")
            eligibility = "declined"
            processed_data["eligibility"] = eligibility

        # 3) Recommendation
        try:
            recommendation = self.recommendation_engine.generate(processed_data)
            logger.info("Recommendation for %r: %r", applicant_id, recommendation)
        except Exception:
            logger.exception("❌ Recommendation generation failed; using fallback text")
            recommendation = "We were unable to generate a recommendation at this time."

        # 4) Final decision
        final_decision = (
            f"Based on our assessment, you are *{eligibility}*. "
            f"Our recommendation: {recommendation}"
        )

        return {
            "eligibility": eligibility,
            "recommendation": recommendation,
            "final_decision": final_decision,
            "processed_data": processed_data,
        }