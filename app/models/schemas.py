from pydantic import BaseModel, Field
from datetime import date
from models.enums import TripStatus

class TripRequest(BaseModel):
    destination_idea: str = Field(max_length=200)
    start_date: date
    end_date: date
    budget: int | None = None

class Activity(BaseModel):
    name: str
    description: str
    estimated_cost: float

class Day(BaseModel):
    day_number: int
    theme: str
    activities: list[Activity]

class TripPlan(BaseModel):
    destination: str
    summary: str
    days: list[Day]

class TripResponse(BaseModel):
    id: int
    status: TripStatus
    plan: TripPlan
