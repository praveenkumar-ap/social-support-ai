import os
import uuid
import logging
from typing import List

from fastapi import APIRouter, HTTPException, status, Depends, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from src.services.db import get_db_session, Applicant, ChatHistory
from src.services.llm_host import LLMClient

logger = logging.getLogger(__name__)
router = APIRouter()


class ChatRequest(BaseModel):
    user_id: str = Field(..., description="ID of the user")
    messages: List[str] = Field(..., min_items=1, description="User messages")
    context: dict = Field(default_factory=dict, description="Optional context")


class ChatResponse(BaseModel):
    responses: List[str] = Field(..., description="Generated chat responses")
    session_id: str = Field(..., description="Chat session identifier")


@router.post("/", response_model=ChatResponse, summary="Chat with the LLM")
async def chat(
    request: Request,
    chat_req: ChatRequest,
    db: Session = Depends(get_db_session),
):
    # 1) Initialize LLM client from env
    llm_host_url = os.getenv("LLM_HOST_URL", "http://llm:11434")
    llm_client = LLMClient(llm_host_url)
    #llm_client = LLMClient()

    # 2) Ensure applicant record exists
    applicant = db.query(Applicant).get(chat_req.user_id)
    if not applicant:
        logger.info(f"Creating new applicant for ID {chat_req.user_id}")
        applicant = Applicant(applicant_id=chat_req.user_id, demographic={})
        db.add(applicant)
        db.commit()

    # 3) Persist the user message
    session_id = str(uuid.uuid4())
    try:
        db.add(
            ChatHistory(
                session_id=session_id,
                applicant_id=chat_req.user_id,
                role="user",
                message=chat_req.messages[-1],
            )
        )
        db.commit()
    except Exception:
        logger.exception("❌ Failed to write user message to chat_history")
        db.rollback()

    # 4) Call LLM
    try:
        responses, llm_session_id = llm_client.chat(
            user_id=chat_req.user_id,
            messages=chat_req.messages,
            context=chat_req.context,
        )
    except HTTPException:
        raise  # pass through 502/504 from client
    except Exception as e:
        logger.exception("❌ Unexpected error calling LLM")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unexpected error calling LLM",
        )

    # 5) Persist the assistant’s reply
    full_response = responses[0] if responses else ""
    try:
        db.add(
            ChatHistory(
                session_id=session_id,
                applicant_id=chat_req.user_id,
                role="assistant",
                message=full_response,
            )
        )
        db.commit()
    except Exception:
        logger.exception("❌ Failed to write assistant reply to chat_history")
        db.rollback()

    # 6) Return a single JSON payload
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"responses": responses, "session_id": session_id},
    )