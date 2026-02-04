"""
Web and Search Skill
Handles web browsing and searching
"""

import webbrowser
from typing import Optional
from .base_skill import BaseSkill, SkillResult

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False


class WebSkill(BaseSkill):
    """Skill for web browsing and searching"""
    
    def can_handle(self, command: str) -> bool:
        """Check if command is about web browsing"""
        web_keywords = ['search', 'open', 'youtube', 'google', 'github', 'website', 'browser']
        return any(keyword in command.lower() for keyword in web_keywords)
    
    def execute(self, command: str, *args, **kwargs) -> Optional[str]:
        """Execute web command"""
        cmd = command.lower()
        
        try:
            if 'search' in cmd:
                query = cmd.replace('search', '').strip()
                return self.search_web(query)
            elif 'youtube' in cmd:
                return self.open_website('youtube.com')
            elif 'google' in cmd:
                return self.open_website('google.com')
            elif 'github' in cmd:
                return self.open_website('github.com')
            elif 'open' in cmd:
                website = cmd.replace('open', '').strip()
                return self.open_website(website)
        except Exception as e:
            self.log(f"Error: {e}")
            return f"Error: {e}"
    
    def search_web(self, query: str) -> str:
        """Search the web for a query"""
        url = f"https://www.google.com/search?q={query}"
        webbrowser.open(url)
        response = f"Searching for {query}"
        self.speak(response)
        return response
    
    def open_website(self, website: str) -> str:
        """Open a specific website"""
        if not website.startswith('http'):
            website = 'https://' + website
        
        webbrowser.open(website)
        response = f"Opening {website}"
        self.speak(response)
        return response
