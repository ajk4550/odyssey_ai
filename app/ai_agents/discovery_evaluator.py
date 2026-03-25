from models.schemas import TripDiscoveryRequest, TripDiscoveryResponse

# Evaluator to evaluate how well the discovery agents suggestions
# match our criteria.
def evaluate(
    response: TripDiscoveryResponse,
    request: TripDiscoveryRequest,
) -> tuple[bool, list[str]]:
    issues = [] # Keeping track of the issues found

    # Criteria Check: Did the LLM return the correct number of responses?
    if len(response.suggestions) != 5:
        issues.append(
            f"Returned {len(response.suggestions)} suggestions instead of 5."
        )

    # Creiteria Check: Did the LLM respect our exclusion list?
    # TODO: There is some edge casing around states. This doesn't catch
    # mappings like New York vs NY. The LLM does have instructions to respect
    # the exclusions so this is passable for now.
    if request.exclude:
        for suggestion in response.suggestions:
            for term in request.exclude:
                if term.lower() in suggestion.destination.lower():
                    issues.append(
                        f'"{suggestion.destination}" violates the "{term}" exclusion.'
                    )

    # Criteria Check: Did the LLM respect the total travel hours
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
