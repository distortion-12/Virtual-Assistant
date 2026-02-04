"""
JARVIS Skills Module
Contains all skills/abilities that JARVIS can perform
"""

from .time_date import TimeAndDateSkill
from .applications import ApplicationSkill
from .system import SystemSkill
from .web import WebSkill
from .files import FileSkill
from .weather import WeatherSkill
from .knowledge import KnowledgeSkill
from .input import InputSkill
from .messages import MessageSkill

__all__ = [
    'TimeAndDateSkill',
    'ApplicationSkill',
    'SystemSkill',
    'WebSkill',
    'FileSkill',
    'WeatherSkill',
    'KnowledgeSkill',
    'InputSkill',
    'MessageSkill',
]
