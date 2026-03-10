from pydantic import BaseModel
from datetime import date

class TripRequest(BaseModel):
    destination_idea: str
    start_date: date
    end_date: date
    budget: int | None = None

class TripResponse(BaseModel):
    id: int
    status: str
