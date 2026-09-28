import requests
from datetime import date
'''
Author:         Jack Kurth
last updated:   12/7/2025

The code uses Python to make an HTTPS request to the Visual Crossing Weather API for fetching timeline weather data in JSON format. 
It constructs a request URL using the start and end date, location, api key.
Using 'requests' library for more robust error handling and more secure connection. 

----Parameters----
        start_date  <object>:   the date of the first day you want to record
        end_date    <object>:   the date of the last day you want to record
        location    <str>:      intended location either ZIP or city name
        API_KEY     <str>:      your personal weather api key can be found at visualcrossing.com  
        flag        <int>:      0 or 1; 0 for json, 1 for request url

    ----Example function call----
        weather_data = api_contents(date(2025, 12, 1), date.today(), "houghton, MI", "XXXXXXXXXXXXXXXXXXXXXXX")

'''

def api_contents(start_date: object, end_date: object, location="Houghton, MI", api_key="XKGQMY2DDCXZWNFF89D2EQQLY", flag=0) -> dict:
    
    # Configuration variables
    base_url = "https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/"
    location = location
    API_KEY = api_key
    unit_group = "us"
    content_type = "json"       
    request_url = f"{base_url}{location}/{start_date}/{end_date}?unitGroup={unit_group}&contentType={content_type}&key={API_KEY}"
    if flag == 0:
        try:
            response = requests.get(request_url)
            # Raise HTTPError if bad response
            response.raise_for_status()
            # Raise HTTPError if bad response
            return response.json()       
        except requests.RequestException as e:
            print(f"\nWeather API request failed--Query Limit Reached: {e}")
            return None

    if flag == 1:
        return request_url
    else:
        print()
        return None
 