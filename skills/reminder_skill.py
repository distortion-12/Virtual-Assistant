import threading
import time
from skills.basic_skills import speak # We need the speak function for the callback

def set_reminder(command: str) -> str:
    """Sets a reminder for a future time."""
    # Example: "remind me to check the oven in 5 minutes"
    try:
        parts = command.split(" in ")
        reminder_text = parts[0].replace("remind me to ", "").strip()
        time_part = parts[1]
        
        delay_seconds = 0
        if "minute" in time_part:
            minutes = int(time_part.split()[0])
            delay_seconds = minutes * 60
        elif "second" in time_part:
            delay_seconds = int(time_part.split()[0])
        else:
            return "Sorry, I can only set reminders in minutes or seconds."

        def reminder_callback():
            speak(f"Reminder: {reminder_text}")

        # Start a timer that runs in the background
        timer = threading.Timer(delay_seconds, reminder_callback)
        timer.start()
        
        return f"Got it. I'll remind you to {reminder_text} in {time_part}."
        
    except Exception as e:
        print(f"Reminder Error: {e}")
        return "I had trouble setting that reminder. Please use the format: 'remind me to [task] in [number] minutes/seconds'."