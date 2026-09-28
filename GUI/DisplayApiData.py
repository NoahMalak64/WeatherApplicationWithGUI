import ApiKeyHandler as handler
import sys, os
from datetime import date

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)
from API.FetchAPIJson import api_contents
"""
python class to do the heavy lifting for returning day summaries to GUI
"""


def displayApiData(location):

    if not isinstance(location, str):
        return None

    weather_data = api_contents(date.today(),date.today(), location, handler.ApiHandler.load_api_key())

    if weather_data is not None and "days" in weather_data and weather_data["days"]:
        for day in weather_data["days"]:
            day_summary = {
                "date":           day.get("datetime"),
                "tempmax":        day.get("tempmax"),
                "tempmin":        day.get("tempmin"),
                "precipitation":  day.get("precip", 0),
                "snow":           day.get("snow", 0),
                "moonphase":      day.get("moonphase"), 
                "description":    day.get("description")
            }

        return day_summary
