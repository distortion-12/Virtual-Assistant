import json
import datetime
import os

LOG_FILE = 'user_habits.json'

def log_habit(command, skill_used):
    """Logs the user's command, the skill it triggered, and the timestamp."""
    log_entry = {
        'timestamp': datetime.datetime.now().isoformat(),
        'command': command,
        'skill': skill_used
    }

    logs = []
    if os.path.exists(LOG_FILE):
        try:
            with open(LOG_FILE, 'r') as f:
                logs = json.load(f)
        except json.JSONDecodeError:
            logs = [] # Start with a fresh list if the file is corrupt

    logs.append(log_entry)

    with open(LOG_FILE, 'w') as f:
        json.dump(logs, f, indent=4)