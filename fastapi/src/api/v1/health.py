from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.db.postgres import get_db_session

router = APIRouter(tags=["health"])

@router.get("/healthz")
async def healthz(db: AsyncSession = Depends(get_db_session)):
    try:
        await db.scalar(select(1))
        return {"status": "ok"}
    except Exception:
        return JSONResponse(status_code=503, content={"status": "error"})
