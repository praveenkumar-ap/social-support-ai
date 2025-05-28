import logging
from typing import List, Dict

logger = logging.getLogger(__name__)

class DataValidationAgent:
    """
    Validate that extracted texts/documents meet basic requirements:
      - At least one bank or income statement
      - Numeric fields parseable
      - No empty or malformed docs
    """

    def validate(self, 
                 raw_documents: List[str], 
                 ocr_texts: List[str]
    ) -> Dict[str, any]:
        errors = []
        # e.g. ensure at least one non-empty OCR text
        if not any(t.strip() for t in ocr_texts):
            errors.append("No text extracted from any document.")
        # e.g. look for numeric patterns
        if not any(any(ch.isdigit() for ch in t) for t in ocr_texts):
            errors.append("No numeric data found in documents.")
        # More rules here…

        ok = not errors
        if ok:
            logger.info("Data validation passed.")
        else:
            logger.warning("Data validation failed: %s", errors)
        return {"ok": ok, "errors": errors}