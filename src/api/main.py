import logging
import time

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.exc import OperationalError

from src.api.routes.health import router as health_router
from src.api.routes.chatbot import router as chatbot_router
from src.api.routes.applications import router as application_router
from src.services.db import Base, engine

# ─── Logging ─────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
)
logger = logging.getLogger(__name__)

# ─── FastAPI App ──────────────────────────────────────────────────────────────
app = FastAPI(
    title="Social Support AI API",
    version="1.0",
    description="Eligibility & streaming chat service",
)

# ─── Enable CORS so Streamlit can call us ────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── Include Routers ──────────────────────────────────────────────────────────
# Health at GET  /health/
app.include_router(health_router, prefix="/health", tags=["Health"])
# Chatbot at POST /chatbot/
app.include_router(chatbot_router, prefix="/chatbot", tags=["Chatbot"])
# Applications at POST /application/
app.include_router(application_router, prefix="/application", tags=["Application"])

# ─── Lifecycle Events ─────────────────────────────────────────────────────────
@app.on_event("startup")
async def on_startup():
    logger.info("🚀 API startup — waiting for database to be ready")
    max_attempts = 10
    delay = 2  # seconds

    # Wait for Postgres to accept connections
    for attempt in range(1, max_attempts + 1):
        try:
            conn = engine.connect()
            conn.close()
            logger.info(f"✅ Database is up (checked in attempt {attempt})")
            break
        except OperationalError:
            logger.warning(
                f"❌ Database not ready (attempt {attempt}/{max_attempts}), retrying in {delay}s..."
            )
            time.sleep(delay)
    else:
        logger.error("❌ Could not connect to database after several attempts")
        raise HTTPException(
            status_code=500,
            detail="Database unavailable, please try again later"
        )

    # Create all tables defined in Base.metadata
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("✅ Database tables are ready")
    except Exception:
        logger.exception("❌ Failed to create database tables")
        raise

@app.on_event("shutdown")
async def on_shutdown():
    logger.info("🛑 API shutdown")