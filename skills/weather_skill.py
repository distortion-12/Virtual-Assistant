import requests
from skills.memory_skills import get_preference, set_preference

def get_weather(location_from_command=None):
    """
    Fetches the weather. If a location is provided, it uses that.
    Otherwise, it uses the saved preferred location. If none exists, it asks.
    """
    location = location_from_command or get_preference("location")

    if not location:
        return "I don't have a location for you yet. What city are you in? You can say, 'my location is [city]'."
    
    try:
        geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={location}"
        geo_response = requests.get(geo_url)
        geo_data = geo_response.json()

        if not geo_data.get('results'):
            return f"Could not find location: {location}"

        lat = geo_data['results'][0]['latitude']
        lon = geo_data['results'][0]['longitude']
        name = geo_data['results'][0]['name']

        # Save the confirmed location as a preference for next time
        set_preference("location", name)

        weather_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true"
        weather_response = requests.get(weather_url)
        weather_data = weather_response.json()

        temperature = weather_data['current_weather']['temperature']
        return f"The current temperature in {name} is {temperature} degrees Celsius."

    except requests.exceptions.RequestException as e:
        return f"Error fetching weather data: {e}"
    except (KeyError, IndexError):
        return "Could not retrieve weather information for the specified location."