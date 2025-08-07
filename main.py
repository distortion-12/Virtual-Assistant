import sys
import threading
import os
import time
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QObject, Signal, Slot
import speech_recognition as sr

import config
from gui import JarvisGUI

# Import all skill functions
from skills.basic_skills import speak, greet, tell_time, tell_date
from skills.automation_skills import open_application, type_text
from skills.web_skills import *
from skills.ai_skills import get_gemini_response
from skills.memory_skills import remember_contextually, recall_info, set_preference, get_preference
from skills.weather_skill import get_weather
from skills.email_skill import read_latest_email
from skills.calendar_skill import get_daily_briefing
from skills.vision_skill import analyze_screen
from skills.conversational_skills import handle_simple_conversation # <-- NEW IMPORT

class AssistantWorker(QObject):
    conversation_updated = Signal(str)
    status_updated = Signal(str)
    orb_state_changed = Signal(str)
    exit_signal = Signal()

    def __init__(self):
        super().__init__()
        self.is_monitoring = True
        self.is_active = False
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        self.recognizer.pause_threshold = 1.5
        with self.microphone as source:
            self.recognizer.adjust_for_ambient_noise(source, duration=1)
        self.api_cooldown_until = 0

    def listen(self):
        status_message = "Listening for command..." if self.is_active else "Listening for wake word..."
        self.status_updated.emit(status_message)
        self.orb_state_changed.emit("listening")
        with self.microphone as source:
            try:
                timeout_duration = 10 if self.is_active else None
                audio = self.recognizer.listen(source, timeout=timeout_duration, phrase_time_limit=5)
            except sr.WaitTimeoutError:
                if self.is_active:
                    self.status_updated.emit("No command heard. Standing by.")
                    self.is_active = False
                return "none"
        try:
            self.status_updated.emit("Recognizing...")
            self.orb_state_changed.emit("thinking")
            query = self.recognizer.recognize_google(audio, language='en-in')
            self.conversation_updated.emit(f"{config.USER_NAME}: {query}")
            return query.lower()
        except (sr.UnknownValueError, sr.RequestError):
            return "none"
        except Exception as e:
            print(f"An error occurred during speech recognition: {e}")
            return "none"

    def speak_and_update_state(self, text):
        self.orb_state_changed.emit("speaking")
        speak(text)
        
    def process_command(self, command: str) -> str | None:
        response = None
        user_name = get_preference("user_name") or config.USER_NAME

        # --- Tier 1: Specific Skills & Preferences ---
        if "my name is" in command:
            name = command.split("my name is")[1].strip()
            set_preference("user_name", name.capitalize())
            response = f"Got it. I'll call you {name.capitalize()} from now on."
        elif "my location is" in command:
            location = command.split("my location is")[1].strip()
            set_preference("location", location)
            response = f"Okay, I'll remember that your location is {location}."
        elif "my favorite news source is" in command:
            source = command.split("my favorite news source is")[1].strip()
            set_preference("news_source", source)
            response = f"I've set {source} as your preferred news source."
        elif "go to sleep" in command or "that's all" in command:
            self.is_active = False
            response = "Understood. Standing by."
        elif 'time' in command:
            response = f"{user_name}, the time is {tell_time()}"
        elif 'date' in command:
            response = f"Today is {tell_date()}"
        # ... (rest of your other specific skills) ...
        elif 'daily briefing' in command or "what's on my schedule" in command:
            response = get_daily_briefing()
        elif 'new email' in command or 'check my email' in command:
            response = read_latest_email()
        elif 'weather' in command:
            location_query = command.replace('weather in', '').replace('weather', '').strip()
            response = get_weather(location_query if location_query else None)
        elif 'news' in command or 'headlines' in command:
            response = get_news_headlines()
        elif 'price of' in command or 'stock price' in command:
            response = get_stock_price(command)
        elif 'translate' in command:
            response = translate_text(command)
        elif 'directions to' in command:
            response = get_directions(command)
        elif 'play' in command and 'youtube' in command:
            response = play_on_youtube(command)
        elif 'search for' in command or 'search' in command:
            response = search_web(command)
        elif 'recycle bin' in command:
            os.system("start shell:RecycleBinFolder")
            response = "Opening Recycle Bin."
        elif 'open' in command:
            response = open_application(command)
        elif 'type' in command or 'write' in command:
            response = type_text(command)
        elif 'wikipedia' in command:
            response = search_wikipedia(command)
        elif 'remember' in command:
            response = remember_contextually(command)
        elif any(word in command for word in ["what do you see", "analyze this", "summarize this", "read this", "analyse my screen", "analyze my screen", "describe my screen", "can you see my screen"]):
            response = analyze_screen(command)
        elif "what's" in command or 'what is' in command or 'what do you know about' in command:
            response = recall_info(command)
        
        # --- Tier 2: Local Conversational AI ---
        elif (simple_response := handle_simple_conversation(command)) is not None:
            response = simple_response

        # --- Tier 3: Fallback to Gemini API ---
        else:
            if command and command != "none":
                if time.time() < self.api_cooldown_until:
                    response = "My AI core is still recharging. Please try a more complex query in a moment."
                else:
                    self.status_updated.emit("Thinking...")
                    self.orb_state_changed.emit("thinking")
                    ai_response = get_gemini_response(command)
                    if "429" in ai_response or "exceeded" in ai_response:
                        response = "I've reached my query limit for now. My AI core needs to recharge for a minute."
                        self.api_cooldown_until = time.time() + 60
                    else:
                        response = ai_response
            else:
                return None

        if response:
            self.speak_and_update_state(response)
            self.conversation_updated.emit(f"{config.ASSISTANT_NAME.upper()}: {response}")

        if 'goodbye' in command or 'exit' in command:
            self.exit_signal.emit()
            return "exit"
        return None

    @Slot(str)
    def process_text_command(self, command: str):
        if not command: return
        self.status_updated.emit("Processing text command...")
        self.conversation_updated.emit(f"{config.USER_NAME} (typed): {command}")
        self.is_active = True
        self.process_command(command.lower())

    @Slot()
    def run_voice_loop(self):
        user_name = get_preference("user_name") or config.USER_NAME
        initial_greeting = greet().replace("Chief", user_name)
        self.conversation_updated.emit(f"{config.ASSISTANT_NAME.upper()}: {initial_greeting}")
        self.speak_and_update_state(initial_greeting)

        while self.is_monitoring:
            if not self.is_active:
                self.orb_state_changed.emit("idle")
            command = self.listen()
            user_name = get_preference("user_name") or config.USER_NAME
            if self.is_active:
                if command and command != "none":
                    if self.process_command(command) == "exit":
                        break
            else:
                if any(word in command for word in config.WAKE_WORDS):
                    self.is_active = True
                    self.speak_and_update_state(f"Yes, {user_name}?")
                    self.conversation_updated.emit(f"{config.ASSISTANT_NAME.upper()}: Yes, {user_name}?")
        self.exit_signal.emit()

def main():
    app = QApplication(sys.argv)
    gui = JarvisGUI()
    worker = AssistantWorker()
    worker.conversation_updated.connect(gui.update_conversation)
    worker.status_updated.connect(gui.update_status)
    worker.orb_state_changed.connect(gui.update_orb_state)
    worker.exit_signal.connect(app.quit)
    gui.text_command_entered.connect(worker.process_text_command)
    voice_thread = threading.Thread(target=worker.run_voice_loop, daemon=True)
    voice_thread.start()
    gui.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()