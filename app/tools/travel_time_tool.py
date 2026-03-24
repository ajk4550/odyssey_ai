import httpx
import logging
from core.config import settings
from agents import function_tool

logger = logging.getLogger(__name__)

ORS_BASE_URL = "https://api.openrouteservice.org"
MODE_MAP = {
    "driving": "driving-car",
    "walking": "foot-walking",
    "cycling": "cycling-regular"
}

@function_tool
async def get_travel_time(origin: str, destination: str, mode: str = "driving") -> dict:
    """Get driving time and distance between two locations.
    Use this when planning travel between cities or locations.
    Mode options: driving, walking, cycling.
    """
    return await _get_travel_time(origin, destination, mode)

async def _get_travel_time(origin: str, destination: str, mode: str = "driving") -> dict:
    # Checking if mode is a valid mode type
    if mode not in MODE_MAP:
        raise ValueError(f"Invalid mode '{mode}'. Choose from: {', '.join(MODE_MAP.keys())}")

    async with httpx.AsyncClient() as client:
        origin_coords = await fetch_geocode(client, origin) # Convert location string to geo-coordinates
        destination_coords = await fetch_geocode(client, destination) # Convert location string to geo-coordinates

        # Building payload which will hit the endpoint.
        payload = {
            "locations": [origin_coords, destination_coords],
            "metrics": ["duration", "distance"]
        }
        headers = {'Authorization': settings.openrouteservice_api_key}

        raw_response = await client.post(f"{ORS_BASE_URL}/v2/matrix/{MODE_MAP[mode]}", json=payload, headers=headers)

        # Handle possible client error
        try:
            raw_response.raise_for_status()
        except httpx.HTTPStatusError as e:
            raise RuntimeError(f"ORS matrix API error: {e.response.status_code}") from e

        response = raw_response.json() # Extract the response into JSON

    # Distance is returned in meters. Converting to miles
    distance_miles = response["distances"][0][1] / 1609.34
    # Duration is returned in seconds. Converting to minutes
    total_minutes = round(response["durations"][0][1] / 60)
    duration_text = _format_duration(total_minutes) # Fetching duration label utilizing hours and minutes

    logger.info(f"Travel time {origin} → {destination}: {total_minutes} min ({round(distance_miles, 1)} miles)")
    return {
        "minutes": total_minutes,
        "duration_text": duration_text,
        "distance_miles": round(distance_miles, 1),
        "mode": mode 
    } 

async def fetch_geocode(client: httpx.AsyncClient, location: str) -> list[float]:
    # Request to openrouteservices to convert location string into geo-coordinates.
    response = await client.get(
        f"{ORS_BASE_URL}/geocode/search",
        params={"api_key": settings.openrouteservice_api_key, "text": location, "size": 1}
    )

    # Handling potential errors in API call
    try:
        response.raise_for_status()
    except httpx.HTTPStatusError as e:
        raise RuntimeError(f"ORS geocoding API error: {e.response.status_code}") from e

    # Checking the validity of the JSON returned
    features = response.json().get("features", [])
    if not features:
        raise ValueError(f"Location not found: {location}")

    # Extracting out the coordinates and returning
    coordinates = features[0]["geometry"]["coordinates"]
    logger.debug(f"Geocoded '{location}' → {coordinates}")
    return coordinates

def _format_duration(total_minutes: int) -> str:
    hours = total_minutes // 60
    minutes = total_minutes % 60

    if hours > 0 and minutes > 0:
        duration_text = f"{hours} hour{'s' if hours > 1 else ''} {minutes} minutes"
    elif hours > 0:
        duration_text = f"{hours} hour{'s' if hours > 1 else ''}"
    else:
        duration_text = f"{minutes} minutes"

    return duration_text

if __name__ == "__main__":
    # Useful for standalone testing of script
    # To call: PYTHONPATH=app python app/tools/travel_time_tool.py
    import asyncio
    logging.basicConfig(level=logging.DEBUG)
    result = asyncio.run(_get_travel_time("Rochester, NY", "Ithaca, NY"))
    print(result)
