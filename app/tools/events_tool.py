# Tool to be used in fetching event info.
# Will fetch attractions (i.e. museums, parks) via the Google Places
# API and events (i.e. concerts and sporting events) via the
# ticketmaster API.
import httpx
import logging
import asyncio
from core.config import settings
from agents import function_tool

logger = logging.getLogger(__name__)

GOOGLE_PLACES_URL = "https://places.googleapis.com/v1/places:searchText"
TICKETMASTER_URL = "https://app.ticketmaster.com/discovery/v2/events.json"
# These are event types that will be excluded from ticketmaster.
# This is to avoid events like post-game events and such.
EXCLUDED_SEGMENTS = {"Miscellaneous", "Undefined"}

@function_tool
async def get_destination_activities(
    destination: str,
    start_date: str,
    end_date: str
) -> dict:
    """Get attractions and events for a destination within a date range.
    Use this when building a trip itinerary to find things to do.
    Returns perennial attractions (museums, landmarks, parks) and
    time-based events (concerts, sports, festivals) happening during the trip.
    """
    return await _get_destination_activities(destination, start_date, end_date)

# Function that acts as the aggregator for the different event sources
async def _get_destination_activities(destination: str, start_date: str, end_date: str) -> dict:
    async with httpx.AsyncClient() as client:
        # asyncio.gather allows both API fetches to run concurrently.
        attractions, events = await asyncio.gather(
            _fetch_attractions(client, destination),
            _fetch_ticketmaster_events(client, destination, start_date, end_date)
        )

    return {
        "attractions": attractions, # Google Places
        "events": events # Ticketmaster
    }

# Function for fetching static attractions from Google Places API
async def _fetch_attractions(client: httpx.AsyncClient, destination: str) -> list[dict]:
    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": settings.google_places_api_key,
        "X-Goog-FieldMask": "places.id,places.displayName,places.types,places.formattedAddress,places.rating"
    }
    payload = {
        "textQuery": f"top tourist attractions in {destination}",
        "maxResultCount": 20 # number of results to return
    }
    raw_response = await client.post(GOOGLE_PLACES_URL, json=payload, headers=headers) 

    try:
        raw_response.raise_for_status()
    except httpx.HTTPStatusError as e:
        raise RuntimeError(f"Google Places API error: {e.response.status_code}") from e

    response = raw_response.json()
    # Get places hash from the response and handle with the possibility of it not existing.
    raw_places = response.get("places", [])

    # Loop through all the places in raw_places and filter to just the data fields we want.
    return [
        {
            "name": place["displayName"]["text"],
            "types": place["types"],
            "rating": place.get("rating"),
            "address": place["formattedAddress"]
        }
        for place in raw_places
    ]

# Function fot fetching ticketed events from Ticketmaster API (i.e. concerts and sporting events)
async def _fetch_ticketmaster_events(
    client: httpx.AsyncClient,
    destination: str,
    start_date: str,
    end_date: str
) -> list[dict]:
    # destination is likely given as "Philadelphia, PA". Ticketmaster wants the city and state.
    destination_parts = destination.split(",")
    city = destination_parts[0].strip()
    state_code = destination_parts[1].strip() if len(destination_parts) > 1 else None

    parameters = {
        "apikey": settings.ticketmaster_api_key,
        "city": city,
        "stateCode": state_code,
        "startDateTime": f"{start_date}T00:00:00Z",
        "endDateTime": f"{end_date}T23:59:59Z",
        "size": 30, # number of results
        "sort": "date,asc",
    }

    raw_response = await client.get(TICKETMASTER_URL, params=parameters)

    try:
        raw_response.raise_for_status()
    except httpx.HTTPStatusError as e:
        raise RuntimeError(f"Ticketmaster API error: {e.response.status_code}") from e

    response = raw_response.json()
    # Try to safely traverse resonse in case no data is returned.
    raw_events = response.get("_embedded", {}).get("events", [])

    # Loop through all the events, filtering out our exclude segments,
    # and try to pull desired data.
    return [
        {
            "name": event["name"],
            "date": event["dates"]["start"]["localDate"],
            "time": event["dates"]["start"].get("localTime"),
            "category": event.get("classifications", [{}])[0].get("segment", {}).get("name"),
            "venue": event["_embedded"]["venues"][0]["name"],
            "url": event.get("url")
        }
        for event in raw_events
        if event.get("classifications", [{}])[0].get("segment", {}).get("name") not in EXCLUDED_SEGMENTS
    ]

if __name__ == "__main__":
    # Useful for standalone testing of script
    # To call: PYTHONPATH=app python app/tools/events_tool.py
    from datetime import date
    from dateutil.relativedelta import relativedelta
    logging.basicConfig(level=logging.DEBUG)
    start = date.today() + relativedelta(months=2) # Use an always future date
    end = start + relativedelta(days=5) # Use future date + 5 for trip range

    result = asyncio.run(_get_destination_activities("Philadelphia, PA", start.isoformat(), end.isoformat()))
    print(result)
