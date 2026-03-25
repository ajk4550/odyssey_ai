from models.schemas import TripDiscoveryRequest

def build_discovery_prompt(request: TripDiscoveryRequest) -> str:
    interests = ", ".join(request.interests) if request.interests else "not specified"
    exclusions = ", ".join(request.exclude) if request.exclude else "none"

    return (
        f"Suggest exactly 5 travel destinations based on the following user-provided criteria:\n"
        f"<user_input>\n"
        f"Origin: {request.origin}\n"
        f"Vacation type: {request.vacation_type}\n"
        f"Month: {request.month}\n"
        f"Budget: ${request.budget}\n"
        f"Interests: {interests}\n"
        f"Exclude: {exclusions}\n"
        f"Max travel time: {f'{request.max_travel_hours} hours' if request.max_travel_hours else 'not specified'}\n"
        f"</user_input>"
    )
