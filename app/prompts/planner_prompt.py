from models.schemas import TripRequest

def build_planner_prompt(trip_request: TripRequest):
    """
    Convert a TripRequest into a structured prompt payload.
    """

    return (
        f"Plan a trip using the following user-provided details:\n"
        f"<user_input>\n"
        f"Origin: {trip_request.origin}\n"
        f"Destination: {trip_request.destination_idea}\n"
        f"Start date: {trip_request.start_date}\n"
        f"End date: {trip_request.end_date}\n"
        f"Budget: ${trip_request.budget}\n"
        f"</user_input>"
    )
