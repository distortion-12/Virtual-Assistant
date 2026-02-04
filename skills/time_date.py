"""
Time and Date Skill
Handles time and date-related queries
"""

from datetime import datetime
from typing import Optional
from .base_skill import BaseSkill, SkillResult


class TimeAndDateSkill(BaseSkill):
    """Skill for handling time and date queries"""
    
    def can_handle(self, command: str) -> bool:
        """Check if command is about time or date"""
        time_keywords = ['time', 'date', 'today', 'current', 'now', 'clock']
        return any(keyword in command.lower() for keyword in time_keywords)
    
    def execute(self, command: str, *args, **kwargs) -> Optional[str]:
        """Execute time/date command"""
        cmd = command.lower()
        
        try:
            if any(word in cmd for word in ['time', 'current time', 'what time', 'what\'s the time']):
                return self.get_time()
            elif any(word in cmd for word in ['date', 'today', 'what\'s today', 'current date']):
                return self.get_date()
            else:
                return self.get_time()
        except Exception as e:
            self.log(f"Error: {e}")
            return f"Error getting time/date: {e}"
    
    def get_time(self) -> str:
        """Get current time"""
        now = datetime.now()
        time_str = now.strftime("%I:%M %p")
        response = f"The current time is {time_str}"
        self.speak(response)
        return response
    
    def get_date(self) -> str:
        """Get current date"""
        now = datetime.now()
        date_str = now.strftime("%A, %B %d, %Y")
        response = f"Today is {date_str}"
        self.speak(response)
        return response
