import json
import datetime
from collections import Counter

LOG_FILE = 'user_habits.json'

def analyze_morning_routine():
    """
    Analyzes logs to find the most common application opened between 8 AM and 10 AM.
    """
    try:
        with open(LOG_FILE, 'r') as f:
            logs = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return None

    morning_commands = []
    for entry in logs:
        log_time = datetime.datetime.fromisoformat(entry['timestamp'])
        # Check for weekdays between 8 AM and 10 AM
        if 8 <= log_time.hour < 10 and log_time.weekday() < 5:
            if entry['skill'] == 'open_application':
                morning_commands.append(entry['command'])

    if not morning_commands:
        return None

    # Find the most common morning command
    most_common_command = Counter(morning_commands).most_common(1)[0][0]
    return most_common_command