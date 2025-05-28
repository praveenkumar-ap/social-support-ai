"""
ValidationAgent: ensures processed data meets schema and data quality checks.
"""

import logging
from typing import Dict, Any

from fastapi import HTTPException, status

logger = logging.getLogger(__name__)

class ValidationAgent:
    def __init__(self):
        """
        Initialize the validation agent.
        """
        pass

    def validate(self, processed_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Perform validation on processed data.
        
        :param processed_data: data from DocumentProcessor
        :return: validated data (may be the same or enriched)
        :raises HTTPException: if validation fails
        """
        try:
            logger.info("ValidationAgent: starting data validation")
            
            # Example check: ensure documents list exists and is not empty
            documents = processed_data.get("documents")
            if documents is None:
                logger.error("ValidationAgent: 'documents' field missing")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Processed data missing 'documents'"
                )
            if not isinstance(documents, list):
                logger.error("ValidationAgent: 'documents' is not a list")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="'documents' must be a list"
                )
            
            # Example check: ensure each document has 'text' key
            for idx, doc in enumerate(documents):
                if "text" not in doc:
                    logger.error(f"ValidationAgent: document at index {idx} missing 'text'")
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Document index {idx} missing 'text'"
                    )
            
            # If all checks pass
            logger.info("ValidationAgent: data validation passed")
            return processed_data

        except HTTPException:
            # propagate HTTP errors
            raise
        except Exception:
            logger.exception("ValidationAgent: unexpected error during validation")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Unexpected validation error"
            )