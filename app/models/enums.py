import enum

class TripStatus(str, enum.Enum):
    pending = "pending"
    processing = "processing"
    completed = "completed"
    failed = "failed"

class ActivityCategory(str, enum.Enum):
    lodging = "lodging"
    food = "food"
    activity = "activity"
    transport = "transport"
    other = "other"

class EvaluationIssueCategory(str, enum.Enum):
    budget = "budget"
    pacing = "pacing"
    exclusions = "exclusions"
    specificity = "specificity"
    meals = "meals"
    variety = "variety"
    day_count = "day_count"
