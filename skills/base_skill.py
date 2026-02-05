"""
Base Skill Class - All skills inherit from this
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional


class BaseSkill(ABC):
    """Base class for all skills"""
    
    def __init__(self, jarvis_instance):
        """Initialize skill with Zenith instance reference"""
        self.jarvis = jarvis_instance
        self.name = self.__class__.__name__
    
    @abstractmethod
    def can_handle(self, command: str) -> bool:
        """Check if this skill can handle the command"""
        pass
    
    @abstractmethod
    def execute(self, command: str, *args, **kwargs) -> Optional[str]:
        """Execute the skill and return result"""
        pass
    
    def speak(self, text: str):
        """Use Zenith to speak"""
        self.jarvis.speak(text)
    
    def log(self, message: str):
        """Log a message"""
        print(f"[{self.name}] {message}")


class SkillResult:
    """Result object for skill execution"""
    
    def __init__(self, success: bool, message: str = "", data: Dict[str, Any] = None):
        self.success = success
        self.message = message
        self.data = data or {}
    
    def __str__(self):
        return self.message
