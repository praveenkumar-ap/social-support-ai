import os
import logging
from typing import Generator

from fastapi import HTTPException, status
from sqlalchemy import (
    create_engine,
    Column, String, Float, Integer, JSON,
    DateTime, ForeignKey, func
)
from sqlalchemy.exc import OperationalError
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

logger = logging.getLogger(__name__)

# ─── Engine & Session Setup ────────────────────────────────────────────
DATABASE_URL = os.environ["POSTGRES_URL"]
engine = create_engine(DATABASE_URL, pool_pre_ping=True, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# ─── ORM Models ────────────────────────────────────────────────────────
class Applicant(Base):
    __tablename__ = "applicants"
    applicant_id = Column(String, primary_key=True, index=True)
    demographic  = Column(JSON, nullable=True)
    created_at   = Column(DateTime(timezone=True),
                          server_default=func.now(),
                          nullable=False)

class Application(Base):
    __tablename__ = "applications"
    application_id = Column(String, primary_key=True, index=True)
    applicant_id   = Column(
        String,
        ForeignKey("applicants.applicant_id", ondelete="CASCADE"),
        nullable=False, index=True
    )
    income         = Column(Float, nullable=False)
    family_size    = Column(Integer, nullable=False)
    eligibility    = Column(String, nullable=False)
    recommendation = Column(String, nullable=False)
    raw_data       = Column(JSON, nullable=False)
    created_at     = Column(DateTime(timezone=True),
                            server_default=func.now(),
                            nullable=False)

class ChatHistory(Base):
    __tablename__ = "chat_history"
    id           = Column(Integer, primary_key=True, autoincrement=True)
    session_id   = Column(String, nullable=False, index=True)
    applicant_id = Column(
        String,
        ForeignKey("applicants.applicant_id", ondelete="CASCADE"),
        nullable=False, index=True
    )
    role         = Column(String, nullable=False)
    message      = Column(String, nullable=False)
    timestamp    = Column(DateTime(timezone=True),
                          server_default=func.now(),
                          nullable=False)

# ─── Dependency: DB session generator ─────────────────────────────────
def get_db_session() -> Generator[Session, None, None]:
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()