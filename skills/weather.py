"""
Weather Skill
Handles weather-related queries
"""

from typing import Optional

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

from .base_skill import BaseSkill, SkillResult


class WeatherSkill(BaseSkill):
    """Skill for weather information"""
    
    def can_handle(self, command: str) -> bool:
        """Check if command is about weather"""
        return 'weather' in command.lower()
    
    def execute(self, command: str, *args, **kwargs) -> Optional[str]:
        """Execute weather command"""
        cmd = command.lower()
        
        # Extract city if mentioned
        city = cmd.replace('weather', '').strip()
        
        return self.get_weather(city if city else "")
    
    def get_weather(self, city: str = "") -> str:
        """Get weather information"""
        if not REQUESTS_AVAILABLE:
            response = "Weather feature not available. Please install requests library."
            self.speak(response)
            return response
        
        api_key = self.jarvis.config.get('weather_api_key', '')
        if not api_key:
            response = "Weather API key not configured"
            self.speak(response)
            return response
        
        if not city:
            city = "London"
        
        try:
            url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
            response_data = requests.get(url, timeout=5)
            data = response_data.json()
            
            if response_data.status_code == 200:
                temp = data['main']['temp']
                desc = data['weather'][0]['description']
                response = f"The temperature in {city} is {temp} degrees celsius with {desc}"
                self.speak(response)
                return response
            else:
                response = "Could not fetch weather information"
                self.speak(response)
                return response
        except Exception as e:
            response = f"Error fetching weather data: {e}"
            self.speak(response)
            return response
