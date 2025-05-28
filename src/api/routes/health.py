from fastapi import APIRouter

router = APIRouter()

@router.get("/", summary="Health check")
async def health():
    """
    Simple health endpoint.
    """
    return {"status": "ok"}