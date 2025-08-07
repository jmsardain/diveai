# from smolagents import tool
import requests 
from io import StringIO
import pandas as pd
from math import radians, cos, sin, asin, sqrt, atan2
import re
# @tool
def get_weather(lat: float, lon: float) -> str:
    """
    Get the weather info for given lat/lon using NOAA (Only US for now). 

    Args:
        lat (float): The latitude of the dive site.
        lon (float): The longitude of the dive site.

    Returns:
        str: The weather info at the dive site.
    """

    base_url = f"https://api.weather.gov/points/{lat},{lon}"
    headers = {"User-Agent": "NOAA-Data-Agent (jadmsardain@gmail.com)"}
    
    try: 
        get_data_api = requests.get(base_url, headers=headers)
        gps_coord_data =  get_data_api.json()

        location_name = gps_coord_data["properties"]["relativeLocation"]["properties"]["city"]
        city = gps_coord_data["properties"]["relativeLocation"]["properties"]["city"]
        parts = [f"Weather in {location_name}"]

        ## Get forecast 
        forecast_url = gps_coord_data["properties"]["forecast"]
        forecast_resp = requests.get(forecast_url, headers=headers)
        forecast_data = forecast_resp.json()["properties"]["periods"][0] ## 0 means tonight

        if forecast_data.get("shortForecast") is not None:
            short_val = forecast_data["shortForecast"]
            parts.append(f"- Overview: {short_val}")
        
        if forecast_data.get("temperature") is not None:
            temp_val = forecast_data["temperature"]
            temp_unit = forecast_data["temperatureUnit"]
            parts.append(f"- Temperature: {temp_val}°{temp_unit}")

        if forecast_data.get("windSpeed")  is not None:
            wind_val = forecast_data["windSpeed"]
            parts.append(f"- Wind speed: {wind_val}")

        if forecast_data.get("windDirection") is not None:
            wind_dir = forecast_data["windDirection"]
            parts.append(f"- Wind direction: {wind_dir}")

        if forecast_data.get("probabilityOfPrecipitation") is not None:
            precip_val = forecast_data["probabilityOfPrecipitation"]["value"]
            parts.append(f"- Probability of precipitation: {precip_val}%")
            
        return "\n".join(parts)

    except Exception as e: 
        return f"Failed to retrieve weather data: {str(e)}" 


# @tool
def get_marine_conditions(lat: float, lon: float) -> str:
    """
    Get the marine conditions info for for given station using NDBC (Only US for now). 

    Args:
        lat (float): The latitude of the dive site.
        lon (float): The longitude of the dive site.

    Returns:
        str: Summary of current marine conditions.
    """

    station_id = find_nearest_buoy(lat, lon)
    if station_id is None:
        return "No nearby marine station found for the given coordinates."

    print(station_id)
    try:
        url = f"https://www.ndbc.noaa.gov/data/latest_obs/{station_id}.txt"
        data = requests.get(url)
        if data.status_code != 200:
            return f"Failed to fetch data for station {station_id}"

        text = data.text

        def extract(pattern, label, units=""):
            match = re.search(pattern, text)
            if match:
                return f"{label}: {match.group(1)} {units}".strip()
            return None

        parts = [f"Marine weather at your location"]

        wave_height     = extract(r"Seas:\s*([\d.]+)", "Wave Height", "ft")
        if wave_height is not None: parts.append(f"- {wave_height}")
        dom_wave_period = extract(r"Peak Period:\s*([\d.]+)", "Dominant Wave Period", "sec")
        if dom_wave_period is not None: parts.append(f"- {dom_wave_period}")
        water_temp      = extract(r"Water Temp:\s*([\d.]+)", "Water Temp (at surface)", "°F")
        if water_temp is not None: parts.append(f"- {water_temp}")
        swell_height    = extract(r"Swell:\s*([\d.]+)", "Swell Height", "ft")
        if swell_height is not None: parts.append(f"- {swell_height}")
        swell_period    = extract(r"Period:\s*([\d.]+)\s*sec", "Swell Period", "sec")
        if swell_period is not None: parts.append(f"- {swell_period}")
        swell_direction = extract(r"Direction:\s*([A-Z]+)", "Swell Direction", "")
        if swell_direction is not None: parts.append(f"- {swell_direction}")
        wind_wave_dir   = extract(r"Wind Wave:\s*([\d.]+)", "Wind Wave Direction", "")
        if wind_wave_dir is not None: parts.append(f"- {wind_wave_dir}")
        

        return "\n".join(parts)

    except Exception as e:
        return f"Error fetching marine data for station {station_id}: {str(e)}"






def haversine(lat1, lon1, lat2, lon2):
    """Calculate the distance (in km) between two lat/lon points."""
    R = 6371  # Earth radius in km
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    lat1 = radians(lat1)
    lat2 = radians(lat2)

    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
    return 2 * R * atan2(sqrt(a), sqrt(1-a))

def find_nearest_buoy(lat, lon):

    stations = load_station_table()
    
    min_dist = float("inf")
    nearest = None

    for _, row in stations.iterrows():
        dist = haversine(lat, lon, row["lat_val"], row["lon_val"])
        if dist < min_dist:
            min_dist = dist
            nearest = row

    if nearest is not None:
        return nearest["station_id"]
    else:
        return 
    # if nearest is not None:
    #     return {
    #         "station_id": nearest["station_id"],
    #         "lat": nearest["lat_val"],
    #         "lon": nearest["lon_val"],
    #         "distance_km": round(min_dist, 2)
    #     }
    # else:
    #     return None



def load_station_table():
    url = "https://www.ndbc.noaa.gov/data/stations/station_table.txt"
    response = requests.get(url)

    # Read raw lines
    lines = response.text.strip().split("\n")

    # Parse each line manually
    rows = []
    
    for idx, line in enumerate(lines):
        if line[0] == "#": continue
        parts = line.strip().split("|")
        if len(parts) < 5:
            continue  # skip malformed lines

        station_id = parts[0]
        location = parts[6]
        gps_location = location.split('(')[0].strip() if '(' in location else location.strip()

        gps_loc = gps_location.strip().split()
        lat_val = float(gps_loc[0])
        lat_dir = gps_loc[1].upper()
        lon_val = float(gps_loc[2])
        lon_dir = gps_loc[3].upper()
        if lat_dir == 'S':
            lat_val = -lat_val
        elif lat_dir != 'N':
            raise ValueError("Invalid latitude direction")

        if lon_dir == 'W':
            lon_val = -lon_val
        elif lon_dir != 'E':
            raise ValueError("Invalid longitude direction")
        rows.append((station_id, lat_val, lon_val))

    df = pd.DataFrame(rows, columns=["station_id", "lat_val", "lon_val"])
    return df

