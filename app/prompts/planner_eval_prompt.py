from models.schemas import TripPlan, TripRequest

def build_planner_eval_prompt(
        trip_plan: TripPlan,
        trip_request: TripRequest
    ) -> str:
    return(
        f"## Trip Request\n"
        f"{trip_request.model_dump_json(indent=2)}\n\n"
        f"## Generated Itinerary\n"
        f"{trip_plan.model_dump_json(indent=2)}\n\n"
        f"Trip duration: {(trip_request.end_date - trip_request.start_date).days + 1} days\n"
        f"Budget: {'Not specified' if trip_request.budget is None else f'${trip_request.budget:,.0f}'} | Estimated total: ${trip_plan.trip_total:.2f}\n\n"
        f"Evaluate the itinerary against the trip request using the criteria in your instructions."
    )
