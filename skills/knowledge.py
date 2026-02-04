"""
Knowledge and Information Skill
Handles knowledge-based queries using Wikipedia and web search
"""

from typing import Optional
from urllib.parse import quote

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

import webbrowser
from .base_skill import BaseSkill, SkillResult


class KnowledgeSkill(BaseSkill):
    """Skill for answering knowledge-based questions"""
    
    def can_handle(self, command: str) -> bool:
        """Check if this is a knowledge question"""
        cmd = command.lower()
        action_keywords = [
            'open', 'launch', 'start', 'close', 'quit', 'exit',
            'create file', 'create folder', 'create directory', 'screenshot',
            'search', 'system', 'cpu', 'memory', 'process',
            'weather', 'time', 'date', 'day',
            'write', 'type', 'enter', 'input',
            'file', 'folder', 'directory',
        ]
        if any(keyword in cmd for keyword in action_keywords):
            return False

        # Fallback: handle general questions
        return True
    
    def execute(self, command: str, *args, **kwargs) -> Optional[str]:
        """Execute knowledge search"""
        return self.search_knowledge(command)
    
    def search_knowledge(self, query: str) -> str:
        """Search for knowledge-based answers using Wikipedia"""
        def _normalize_query(q: str) -> str:
            q = q.strip().lower()
            prefixes = [
                "who is ", "what is ", "why is ", "how is ",
                "who are ", "what are ", "why are ", "how are ",
                "tell me about ", "information about ",
            ]
            for p in prefixes:
                if q.startswith(p):
                    q = q[len(p):]
                    break
            return q.strip(" ?!.,") or q

        query = _normalize_query(query)
        headers = {
            "User-Agent": "Jarvis/1.0 (https://example.com; contact: local)"
        }
        if not REQUESTS_AVAILABLE:
            return self.fallback_search(query)
        
        try:
            # First, find the best matching Wikipedia title
            search_url = "https://en.wikipedia.org/w/api.php"
            search_params = {
                'action': 'opensearch',
                'format': 'json',
                'search': query,
                'limit': 1,
            }
            search_response = requests.get(search_url, params=search_params, headers=headers, timeout=5)
            search_data = search_response.json()
            title = None
            if isinstance(search_data, list) and len(search_data) >= 2 and search_data[1]:
                title = search_data[1][0]

            # Try to get answer from Wikipedia API
            url = "https://en.wikipedia.org/w/api.php"
            params = {
                'action': 'query',
                'format': 'json',
                'titles': title or query,
                'prop': 'extracts',
                'explaintext': True,
                'exintro': True,
            }
            
            response = requests.get(url, params=params, headers=headers, timeout=5)
            data = response.json()
            
            # Extract the page content
            pages = data.get('query', {}).get('pages', {})
            for page_id, page_data in pages.items():
                if 'extract' in page_data and page_data['extract']:
                    extract = page_data['extract']
                    # Get first 2-3 sentences
                    sentences = extract.split('.')[:3]
                    answer = '.'.join(sentences).strip()
                    
                    self.speak(answer)
                    return answer

            # Fallback: Wikipedia REST summary
            if title:
                summary_url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{quote(title)}"
            else:
                summary_url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{quote(query)}"
            summary_response = requests.get(summary_url, headers=headers, timeout=5)
            if summary_response.status_code == 200:
                summary_data = summary_response.json()
                summary_text = summary_data.get('extract')
                if summary_text:
                    self.speak(summary_text)
                    return summary_text
            
            # If no Wikipedia result, fallback to web search
            return self.fallback_search(query)
            
        except Exception as e:
            self.log(f"Error searching knowledge: {e}")
            return self.fallback_search(query)
    
    def fallback_search(self, query: str) -> str:
        """Fallback to web search"""
        response = (
            f"I couldn't find a concise answer for {query}. "
            "Try rephrasing, or say 'search' followed by your query to open the web."
        )
        self.speak(response)
        return response
