from models.schemas import TripDiscoveryRequest, TripDiscoveryResponse

def evaluate(
    response: TripDiscoveryResponse,
    request: TripDiscoveryRequest,
) -> tuple[bool, list[str]]:
    issues = []

    if len(response.suggestions) != 5:
        issues.append(
            f"Returned {len(response.suggestions)} suggestions instead of 5."
        )

    if request.exclude:
        for suggestion in response.suggestions:
            for term in request.exclude:
                if term.lower() in suggestion.destination.lower():
                    issues.append(
                        f'"{suggestion.destination}" violates the "{term}" exclusion.'
                    )

    if request.max_travel_hours:
        limit_minutes = request.max_travel_hours * 60
        for suggestion in response.suggestions:
            if suggestion.travel_time_minutes > limit_minutes:
                issues.append(
                    f'"{suggestion.destination}" has a travel time of '
                    f"{suggestion.travel_time_minutes} minutes, which exceeds "
                    f"the {request.max_travel_hours} hour limit."
                )

    return len(issues) == 0, issues
