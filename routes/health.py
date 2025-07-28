# routes/health.py
from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def health():
    return {"status": "app running successfully! healthy"}