import os
import requests
# from smolagents import tool

def get_marine_life(lat: float, lon: float) -> str:
    """
    Get common marine life at a dive site using iNaturalist API.
    
    Args:
        lat (float): The latitude of the dive site.
        lon (float): The longitude of the dive site.
    
    Returns:
        str: The common marine life at a dive site.
    """
    url = "https://api.inaturalist.org/v1/observations"
    
    # Parameters for marine observations near the coordinates
    params = {
        "lat": lat,
        "lng": lon,
        "radius": 20,  # 10km radius
        "taxon_id": 47115,  # Marine animals taxon ID
        "per_page": 20,
        "order": "desc",
        "order_by": "created_at"
    }
    
    try:
        resp = requests.get(url, params=params, timeout=10)
        print(f"Full URL: {resp.url}")
        resp.raise_for_status()
        data = resp.json()
        
        if not data.get("results") or len(data["results"]) == 0:
            return "No marine life observations found in this area."
        
        # Extract unique species names
        species = set()
        for obs in data["results"]:
            if obs.get("taxon") and obs["taxon"].get("name"):
                species.add(obs["taxon"]["name"])
        
        if not species:
            return "No marine species identified in this area."
        
        # Return up to 8 most common species
        species_list = list(species)[:8]
        species_formatted = '\n'.join([f"• {species}" for species in species_list])
        return f"Common marine life:\n{species_formatted}"
        
    except Exception as e:
        return f"Error fetching marine life data: {e}"