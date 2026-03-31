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
