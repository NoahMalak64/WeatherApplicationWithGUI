from FetchAPIJson import api_contents
from datetime import timedelta, date
import json
import os

"""
Author:         jack Kurth
last updated:   12/3/2025

Grabs daily weather data in the form of;

    "2025-12-03": [
        {
            "location": "houghton, mi",
            "datetime": "2025-12-03",
            "tempmax": 26.2,
            "tempmin": 9.9,
            "average_temp": 18.5,
            "precipitation": 0.083,
            "snow": 0.6,
            "moonphase": 0.46
        }
    ]

and sends all data to cleanData.json. 
Data then gets parsed for graphing purposes.
This code can be found at github repo: NoahMalak64/TeamSoftwareProd 

    ----Parameters----
        start_date  <object>:   the date of the first day you want to record
        end_date    <object>:   the date of the last day you want to record
        location    <str>:      intended location either ZIP or city name
        API_KEY     <str>:      your personal weather api key can be found at visualcrossing.com  

    ----Example function call----
        start_date = date(2025, 12, 1)
        end_date = date(2025, 12, 17)
        fetch_clean_data(start_date, end_date, "houghton, MI)
"""

def fetch_clean_data(start_date: object, end_date: object, location: str, api_key: str) -> dict: 

    e_str = """
    ----Parameters----
        start_date  <object>:   the date of the first day you want to record
        end_date    <object>:   the date of the last day you want to record
        location    <str>:      intended location either ZIP or city name
        API_KEY     <str>:      your personal weather api key can be found at visualcrossing.com  
    """

    if not isinstance(start_date, date) or not isinstance(end_date, date):
        raise TypeError(e_str)
    if start_date > end_date:
        raise ValueError(e_str)
    if not isinstance(location, str) or not location.strip():
        raise ValueError(e_str)
    if not isinstance(api_key, str) or not api_key.strip():
        raise ValueError(e_str)

    base_dir = os.path.dirname(os.path.abspath(__file__))
    json_path = os.path.normpath(os.path.join(base_dir, "..", "json/cleanData.json"))
    os.makedirs(os.path.dirname(json_path), exist_ok=True)

     # Load existing data if the file already exists
    existing_data = {}
    if os.path.exists(json_path):
        try:
            with open(json_path, mode="r", encoding="utf-8") as jf:
                existing_data = json.load(jf) or {}
        except (json.JSONDecodeError, OSError):
            # If file is empty, start fresh
            existing_data = {}

    # store per-day summary 
    data_by_date = {}
    API_KEY = api_key
    while start_date <= end_date:
        remaining = (end_date - start_date).days + 1
        chunk_days = min(15, remaining)
        next_date = start_date + timedelta(days=chunk_days - 1)
        # this grabs the entire json from the API--this is important it is parsed below
        weather_data = api_contents(start_date, next_date, location, API_KEY) 
        if weather_data is not None and "days" in weather_data:
            location = str(weather_data.get("address", "")).lower()
            for day in weather_data["days"]:
                dt = day.get("datetime")
                # this is where the data gets parsed and added to a dict that will be appended to the json file
                day_summary = {
                    "location": location,
                    "datetime": dt,
                    "tempmax": day.get("tempmax"),
                    "tempmin": day.get("tempmin"),
                    "average_temp": day.get("temp"),
                    "precipitation": day.get("precip", 0),
                    "snow": day.get("snow", 0),
                    "moonphase": day.get("moonphase"),
                }
                data_by_date.setdefault(dt, []).append(day_summary)
            print(f"\nSaved {len(weather_data['days'])} day(s) from {start_date} -> {next_date}\n")
        else:
            print(f"No data returned for {start_date} -> {next_date}")
        start_date = next_date + timedelta(days=1)

                # Merge new data into existing_data but check for duplicates on (date, location)
        for dt, entries in data_by_date.items():
            # Ensure we have a list at this date key
            if dt not in existing_data or not isinstance(existing_data[dt], list):
                existing_data[dt] = []

            existing_list = existing_data[dt]

            for new_entry in entries:
                new_loc = new_entry.get("location")
                new_dt  = new_entry.get("datetime")

                # Check if there is already an entry with same date AND location
                is_dup = any(
                    (e.get("location") == new_loc and e.get("datetime") == new_dt)
                    for e in existing_list
                )

                if is_dup:
                    print(f"duplicate found for {new_dt} at {new_loc}")  # optional logging
                else:
                    existing_list.append(new_entry)

        # Write merged result back to file
        with open(json_path, mode="w", encoding="utf-8") as jf:
            json.dump(existing_data, jf, ensure_ascii=False, indent=4)



fetch_clean_data(date(2025, 12, 7), date(2025, 12, 14), "Detriot, MI", "XKGQMY2DDCXZWNFF89D2EQQLY")