from pydantic import BaseModel, Field, computed_field
from datetime import date
from models.enums import TripStatus, ActivityCategory, EvaluationIssueCategory
from typing import Literal

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
    category: ActivityCategory
    estimated_cost: float

class Day(BaseModel):
    day_number: int
    theme: str
    activities: list[Activity]

    @computed_field
    @property
    def daily_total(self) -> float:
        return sum(a.estimated_cost for a in self.activities)

class TripPlan(BaseModel):
    destination: str
    summary: str
    days: list[Day]

    @computed_field
    @property
    def trip_total(self) -> float:
        return sum(day.daily_total for day in self.days)

    @computed_field
    @property
    def category_totals(self) -> dict[str, float]:
        totals: dict[str, float] = {}
        for day in self.days:
            for activity in day.activities:
                totals[activity.category] = totals.get(activity.category, 0) + activity.estimated_cost
        return totals

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

class EvaluationIssue(BaseModel):
    severity: Literal["blocking", "warning"]
    category: EvaluationIssueCategory
    description: str

class PlanEvaluation(BaseModel):
    passed: bool
    issues: list[EvaluationIssue]
