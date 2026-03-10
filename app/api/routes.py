from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from models.schemas import TripRequest, TripResponse
from db.session import get_db

router = APIRouter(prefix="/api/v1", tags=["trips"])

@router.post("/plan-trip", response_model=TripResponse)
async def plan_trip(request: TripRequest, db: AsyncSession = Depends(get_db)):
    return { "id": 1, "status": "pending" }
