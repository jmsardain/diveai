import os
import requests
# from smolagents import tool

# @tool
def get_dive_sites(lat: float, lon: float) -> str:
    """
    Get the dive site available at a certain lat and lon using the World Scuba Diving Sites API.
    Args:
        lat (float): The latitude of the dive site.
        lon (float): The longitude of the dive site.
    Returns:
        str: Returns a summary of dive sites near lat/lon.
    """
    api_key = os.getenv("RAPIDAPI_KEY")
    url = "https://world-scuba-diving-sites-api.p.rapidapi.com/divesites/gps"
    headers = {
        "X-RapidAPI-Key": api_key,
        "X-RapidAPI-Host": "world-scuba-diving-sites-api.p.rapidapi.com"
    }
    # Define a small bounding box around the point (±0.1 degrees)
    delta = 0.02
    params = {
        "southWestLat": lat,
        "northEastLat": lat + delta,
        "southWestLng": lon,
        "northEastLng": lon + delta
    }
    try:
        resp = requests.get(url, headers=headers, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        # New API format: {"success":true, "data": [ ... ]}
        if not data.get("success") or not isinstance(data.get("data"), list) or not data["data"]:
            return "No dive sites found nearby."
        # Summarize up to 3 sites
        sites = []
        for site in data["data"][:3]:
            name = site.get("name", "Unknown Site")
            latitude = site.get("latitude", "?")
            longitude = site.get("longitude", "?")
            sites.append(f"{name}:\n    Lat: {latitude}\n    Lon: {longitude}")
        return "Nearby sites:\n" + "\n\n".join(sites)
    except Exception as e:
        return f"Error fetching dive sites: {e}"

    # return "Marine life"
