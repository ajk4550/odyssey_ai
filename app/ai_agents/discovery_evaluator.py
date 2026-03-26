from models.schemas import TripDiscoveryRequest, TripDiscoveryResponse

# State map and reverse will be used to check whether LLM returned a state that was
# to be excluded. The mapping is to catch both NY and New York (for example)
_STATE_MAP = {
    "alabama": "al", "alaska": "ak", "arizona": "az", "arkansas": "ar",
    "california": "ca", "colorado": "co", "connecticut": "ct", "delaware": "de",
    "florida": "fl", "georgia": "ga", "hawaii": "hi", "idaho": "id",
    "illinois": "il", "indiana": "in", "iowa": "ia", "kansas": "ks",
    "kentucky": "ky", "louisiana": "la", "maine": "me", "maryland": "md",
    "massachusetts": "ma", "michigan": "mi", "minnesota": "mn", "mississippi": "ms",
    "missouri": "mo", "montana": "mt", "nebraska": "ne", "nevada": "nv",
    "new hampshire": "nh", "new jersey": "nj", "new mexico": "nm", "new york": "ny",
    "north carolina": "nc", "north dakota": "nd", "ohio": "oh", "oklahoma": "ok",
    "oregon": "or", "pennsylvania": "pa", "rhode island": "ri", "south carolina": "sc",
    "south dakota": "sd", "tennessee": "tn", "texas": "tx", "utah": "ut",
    "vermont": "vt", "virginia": "va", "washington": "wa", "west virginia": "wv",
    "wisconsin": "wi", "wyoming": "wy"
}
_REVERSE_STATE_MAP = {v: k for k, v in _STATE_MAP.items()}

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
    if request.exclude:
        for suggestion in response.suggestions:
            for term in request.exclude:
                # Extra logic here is to handle state permutations. If the user excludes
                # New York, we need to exclude ny as well. Helper function returns
                # alternates that we can check against.
                check_terms = _resolve_exclusion_terms(term) # Get alternate forms for states
                destination_lower = suggestion.destination.lower()
                if any(t in destination_lower for t in check_terms):
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

def _resolve_exclusion_terms(term: str) -> list[str]:
    # term will be an exclusion term such as New York. Normalize it:
    normalized = term.lower().strip() # i.e. new york
    # Build a new array to hold permutations. Start with
    # normalized term
    terms = [normalized] # i.e. ["new york"]

    if normalized in _STATE_MAP:
        # If our normalized term (new york) is in the states map, get
        # its alternate abbreviated form and add to our terms array.
        terms.append(_STATE_MAP[normalized])

    if normalized in _REVERSE_STATE_MAP:
        # If our normalized term (ny) is in the reversed states array,
        # get the alternate form (new york) and add it to terms array.
        terms.append(_REVERSE_STATE_MAP[normalized])

    # Return an array that has the states permutations
    return terms
