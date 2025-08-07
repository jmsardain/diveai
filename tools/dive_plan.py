# from smolagents import tool
from typing import List, Dict, Any

# @tool
def calculate_dive_profile(
    tank_size_l: float,
    o2_percent: float,
    start_pressure_bar: float,
    bottom_time_min: float,
    depth_m: float,
    sac_rate: float = 20.0,
    reserve_bar: float = 50.0,
) -> Dict[str, Any]:
    """
    Calculate a simple dive profile and waypoints for a recreational dive.

    Args:
        tank_size_l (float): Size of the tank in liters.
        o2_percent (float): Oxygen percentage in the tank.
        start_pressure_bar (float): Starting pressure in the tank (bar).
        bottom_time_min (float): Planned bottom time (min).
        depth_m (float): Planned depth (m).
        sac_rate (float): Surface Air Consumption rate (L/min at 1 ATA).
        reserve_bar (float): Reserve pressure to keep in tank (bar).

    Returns:
        dict: Dive profile summary and waypoints.
    """
    # Calculate available gas (usable)
    usable_gas_l = tank_size_l * max(0, start_pressure_bar - reserve_bar)

    # Waypoints: descent, bottom, ascent, safety stop
    descent_rate = 18  # m/min
    ascent_rate = 9    # m/min
    safety_stop_depth = 5  # m
    safety_stop_time = 3   # min

    # Descent
    descent_time = depth_m / descent_rate
    descent_avg_depth = depth_m / 2
    descent_pressure = (descent_avg_depth / 10) + 1
    descent_gas = sac_rate * descent_pressure * descent_time

    # Bottom
    bottom_pressure = (depth_m / 10) + 1
    bottom_gas = sac_rate * bottom_pressure * bottom_time_min

    # Ascent
    ascent_time = (depth_m - safety_stop_depth) / ascent_rate if depth_m > safety_stop_depth else 0
    ascent_avg_depth = (depth_m + safety_stop_depth) / 2 if depth_m > safety_stop_depth else depth_m / 2
    ascent_pressure = (ascent_avg_depth / 10) + 1
    ascent_gas = sac_rate * ascent_pressure * ascent_time

    # Safety stop
    safety_stop_pressure = (safety_stop_depth / 10) + 1
    safety_stop_gas = sac_rate * safety_stop_pressure * safety_stop_time

    # Total gas used
    total_gas = descent_gas + bottom_gas + ascent_gas + safety_stop_gas
    remaining_gas = usable_gas_l - total_gas

    # Build waypoints
    waypoints = [
        {"depth_m": 0, "duration_min": 0, "description": "Surface Start"},
        {"depth_m": depth_m, "duration_min": round(descent_time, 2), "description": "Descent"},
        {"depth_m": depth_m, "duration_min": bottom_time_min, "description": "Bottom"},
        {"depth_m": safety_stop_depth, "duration_min": round(ascent_time, 2), "description": "Ascent to Safety Stop"},
        {"depth_m": safety_stop_depth, "duration_min": safety_stop_time, "description": "Safety Stop"},
        {"depth_m": 0, "duration_min": 0, "description": "Surface End"},
    ]

    profile = {
        "tank_size_l": tank_size_l,
        "o2_percent": o2_percent,
        "start_pressure_bar": start_pressure_bar,
        "reserve_bar": reserve_bar,
        "usable_gas_l": round(usable_gas_l, 1),
        "total_gas_used_l": round(total_gas, 1),
        "remaining_gas_l": round(remaining_gas, 1),
        "sac_rate_l_min": sac_rate,
        "max_depth_m": depth_m,
        "bottom_time_min": bottom_time_min,
        "waypoints": waypoints,
        "warning": None,
    }
    if remaining_gas < 0:
        profile["warning"] = "Planned dive exceeds available gas!"

    return {"profile": profile, "waypoints": waypoints}