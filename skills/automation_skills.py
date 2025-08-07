from AppOpener import open as open_app
import pyautogui
from skills.basic_skills import speak # Import speak from basic_skills

def open_application(command):
    """Opens an application by name."""
    app_name = command.replace("open", "").strip()
    speak(f"Opening {app_name} for you, Chief.")
    try:
        open_app(app_name, match_closest=True)
    except Exception as e:
        speak(f"Sorry, I couldn't find the application {app_name}. Please make sure it's installed.")

def type_text(command):
    """Types out the given text."""
    text_to_type = command.replace("type", "").replace("write", "").strip()
    if text_to_type:
        speak(f"Typing: {text_to_type}")
        pyautogui.write(text_to_type, interval=0.1)
    else:
        speak("What should I type?")
        # In a real scenario, you'd call the listen() function here.
        # For now, we'll just show a message.
        speak("Please provide the text you want me to type.")