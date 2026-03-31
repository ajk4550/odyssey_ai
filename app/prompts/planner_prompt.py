from models.schemas import TripRequest

def build_planner_prompt(trip_request: TripRequest):
    """
    Convert a TripRequest into a structured prompt payload.
    """
    interests = ", ".join(trip_request.interests) if trip_request.interests else "not specified"
    exclusions = ", ".join(trip_request.exclude) if trip_request.exclude else "none"

    return (
        f"Plan a trip using the following user-provided details:\n"
        f"<user_input>\n"
        f"Origin: {trip_request.origin}\n"
        f"Destination: {trip_request.destination_idea}\n"
        f"Start date: {trip_request.start_date}\n"
        f"End date: {trip_request.end_date}\n"
        f"Budget: ${trip_request.budget}\n"
        f"Interests: {interests}\n"
        f"Exclusions: {exclusions}\n"
        f"</user_input>"
        f"<instructions>\n"
        f"- The budget is a target to plan toward. Your itinerary should utilize close to the full ${trip_request.budget}.\n"
        f"- Include a lodging activity for every night of the trip. Each night should have its own entry — do not consolidate multiple nights into one.\n"
        f"</instructions>"
    )
