from pydantic import BaseModel, Field
from datetime import date
from models.enums import TripStatus

class TripRequest(BaseModel):
    origin: str = Field(max_length=200)
    destination_idea: str = Field(max_length=200)
    start_date: date
    end_date: date
    budget: int | None = None
    interests: list[str] | None = None
    exclude: list[str] | None = None

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

class TripDiscoveryRequest(BaseModel):
    origin: str = Field(max_length=1000)
    vacation_type: str = Field(max_length=1000)
    month: str
    budget: int | None = None
    interests: list[str] | None = None
    exclude: list[str] | None = None
    max_travel_hours: int | None = None

class DestinationSuggestion(BaseModel):
    destination: str
    reason: str
    estimated_travel_time: str
    travel_time_minutes: int

class TripDiscoveryResponse(BaseModel):
    suggestions: list[DestinationSuggestion]
