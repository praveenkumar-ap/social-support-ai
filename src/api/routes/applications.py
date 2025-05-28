"""
Applications routes for Social Support AI API.
"""
import logging
from uuid import uuid4
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from src.services.db import get_db_session, Applicant, Application


from src.services.db import (
    get_db_session,
    Applicant,
    Application,
)
from src.core.agent_orchestrator import AgentOrchestrator

logger = logging.getLogger(__name__)
router = APIRouter()

# ----------------------------
# Pydantic models
# ----------------------------
class ApplicationRequest(BaseModel):
    applicant_id: str = Field(..., description="Unique applicant identifier")
    income: float = Field(..., description="Applicant monthly income")
    family_size: int = Field(..., description="Number of family members")
    documents: List[str] = Field(..., description="Base64-encoded document data URIs")

class ApplicationResponse(BaseModel):
    application_id: str = Field(..., description="Generated application record ID")
    eligibility: str = Field(..., description="Eligibility decision")
    recommendation: str = Field(..., description="Enablement recommendation")
    final_decision: str = Field(..., description="Combined final decision message")

# ----------------------------
# Routes
# ----------------------------
@router.post(
    "/", response_model=ApplicationResponse, status_code=status.HTTP_201_CREATED
)
async def submit_application(
    req: ApplicationRequest,
    db: Session = Depends(get_db_session)
) -> ApplicationResponse:
    """
    Submit a social support application.
    """
    logger.info(f"Received application for applicant {req.applicant_id}")

    try:
        # 1) Ensure applicant exists
        applicant = db.query(Applicant).get(req.applicant_id)
        if not applicant:
            applicant = Applicant(
                applicant_id=req.applicant_id,
                demographic={},  # you could populate from context if available
            )
            db.add(applicant)
            db.flush()  # ensure applicant_id is present

        # 2) Run business logic
        orchestrator = AgentOrchestrator()
        result = orchestrator.run(
            applicant_id=req.applicant_id,
            documents=req.documents,
            income=req.income,
            family_size=req.family_size
        )

        # 3) Persist application record
        app_id = str(uuid4())
        application = Application(
            application_id=app_id,
            applicant_id=req.applicant_id,
            income=req.income,
            family_size=req.family_size,
            eligibility=result["eligibility"],
            recommendation=result["recommendation"],
            raw_data={
                "documents": req.documents,
                **result.get("processed_data", {})
            }
        )
        db.add(application)
        db.commit()
        logger.info(f"Application {app_id} saved to database")

        return ApplicationResponse(
            application_id=app_id,
            eligibility=result["eligibility"],
            recommendation=result["recommendation"],
            final_decision=result["final_decision"]
        )

    except Exception:
        logger.exception("Error processing application")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process application"
        )