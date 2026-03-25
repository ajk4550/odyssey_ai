from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from models.schemas import TripRequest, TripResponse, TripDiscoveryRequest, TripDiscoveryResponse
from models.db_models import Trip
from models.enums import TripStatus
from db.session import get_db
from ai_agents.planner_agent import PlannerAgent
from ai_agents.discovery_agent import DiscoveryAgent

router = APIRouter(prefix="/api/v1", tags=["trips"])

@router.post("/plan-trip", response_model=TripResponse)
async def plan_trip(request: TripRequest, db: AsyncSession = Depends(get_db)):
    # Save the initial record to DB
    trip = Trip(user_input=request.model_dump(mode="json"), status=TripStatus.pending)
    db.add(trip)
    await db.commit()
    await db.refresh(trip)

    # Mark record as in progress
    trip.status = TripStatus.processing
    await db.commit()

    # Try to generate the trip plan from the AI Agent
    try:
        trip_plan = await PlannerAgent.generate_plan(request)
    except Exception:
        trip.status = TripStatus.failed
        await db.commit()
        raise HTTPException(status_code=500, detail="Trip planning failed. Please try again later.")

    # Save the results
    trip.status = TripStatus.completed
    trip.result = trip_plan.model_dump()
    await db.commit()
    await db.refresh(trip)

    return { "id": trip.id, "status": trip.status, "plan": trip_plan }

@router.post("/suggest-destinations", response_model=TripDiscoveryResponse)
async def suggest_destinations(request: TripDiscoveryRequest):
    try:
        return await DiscoveryAgent.generate_suggestions(request)
    except Exception:
        raise HTTPException(status_code=500, detail="Destination discovery failed. Please try again later.")
