import datetime
import pyttsx3

# --- Initialize the TTS Engine ---
engine = pyttsx3.init('sapi5')
voices = engine.getProperty('voices')
# You can experiment with different voices. voices[0] is typically male, voices[1] is female.
engine.setProperty('voice', voices[1].id)

# --- Adjust Speaking Rate ---
# The default rate is usually 200. Lowering it makes the speech slower and clearer.
# A value around 170-180 is often a good starting point for a more conversational pace.
engine.setProperty('rate', 175)


def speak(text):
    """This function takes text and speaks it out using the configured engine."""
    print(f"LYRA: {text}")
    engine.say(text)
    engine.runAndWait()

def greet():
    """Greets the user based on the time of day."""
    hour = int(datetime.datetime.now().hour)
    if 0 <= hour < 12:
        return "Good Morning, Chief! Welcome back!"
    elif 12 <= hour < 18:
        return "Good Afternoon, Chief! welcome back!"
    else:
        return "Good Evening, Chief! Welcome back!"

def tell_time():
    """Tells the current time."""
    return datetime.datetime.now().strftime("%I:%M %p")

def tell_date():
    """Tells the current date."""
    return datetime.datetime.now().strftime("%B %d, %Y")
