from flask import Flask, render_template, request
from agent import get_dive_plan
import os 
import re

app = Flask(__name__)

token = os.getenv("HUGGINGFACE_HUB_TOKEN")

def parse_result_sections(result_str):
    # Split the result string into sections by header
    sections = {
        'weather': '',
        'marine_conditions': '',
        'dive_plan': '',
        'dive_sites': '',
        'marine_life': ''
    }
    if not result_str:
        return sections
    # Use regex to find each section
    pattern = re.compile(r"Weather:(.*?)Marine conditions:(.*?)Dive plan:(.*?)Dive sites:(.*?)Marine life:(.*)", re.DOTALL)
    match = pattern.search(result_str)
    if match:
        sections['weather'] = match.group(1).strip()
        sections['marine_conditions'] = match.group(2).strip()
        sections['dive_plan'] = match.group(3).strip()
        sections['dive_sites'] = match.group(4).strip()
        sections['marine_life'] = match.group(5).strip()
    else:
        # fallback: put everything in dive_plan
        sections['dive_plan'] = result_str
    return sections

@app.route("/", methods=["GET", "POST"])
def index():
    result = {}
    if request.method == "POST":
        lat = request.form["lat"]
        lon = request.form["lon"]
        tank_size_l = request.form["tank_size_l"]
        o2_percent = request.form["o2_percent"]
        start_pressure_bar = request.form["start_pressure_bar"]
        bottom_time_min = request.form["bottom_time_min"]
        depth_m = request.form["depth_m"]

        # Call the direct API version of get_dive_plan
        result_str = get_dive_plan(
            lat=float(lat),
            lon=float(lon),
            tank_size_l=float(tank_size_l),
            o2_percent=float(o2_percent),
            start_pressure_bar=float(start_pressure_bar),
            bottom_time_min=float(bottom_time_min),
            depth_m=float(depth_m),
        )
        result = parse_result_sections(result_str)
    return render_template("index.html", result=result)

if __name__ == "__main__":
    app.run(debug=True)
