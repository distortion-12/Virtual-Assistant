import random

def handle_simple_conversation(command: str):
    """
    Handles simple, non-critical conversational commands locally to save API calls.
    Returns a response string if a command is handled, otherwise returns None.
    """
    # --- Identity and Capability Questions ---
    if "who are you" in command or "what are you" in command:
        return "I am LYRA, a desktop AI assistant designed to help you with various tasks."
    
    if "what can you do" in command:
        return "I can open applications, search the web, tell you the time, date, and weather, manage notes, and answer questions. What would you like me to do?"

    # --- Simple pleasantries ---
    if "good morning" in command:
        return "Good morning! I hope you have a productive day."
    if "good afternoon" in command:
        return "Good afternoon. How can I help you?"
    if "good evening" in command:
        return "Good evening. I hope you've had a pleasant day."

    # --- Fun/Creative Commands ---
    if "tell me a joke" in command:
        jokes = [
            "Why don't scientists trust atoms? Because they make up everything!",
            "I told my wife she was drawing her eyebrows too high. She looked surprised.",
            "Why did the scarecrow win an award? Because he was outstanding in his field."
        ]
        return random.choice(jokes)
    
    # --- Simple Math ---
    # A very basic math parser. Be cautious with eval in a real-world app.
    if any(op in command for op in ["plus", "minus", "times", "divided by"]):
        try:
            command = command.replace("what is", "").strip()
            command = command.replace("plus", "+").replace("minus", "-").replace("times", "*").replace("divided by", "/")
            result = eval(command)
            return f"The answer is {result}."
        except Exception:
            return "I can only handle basic math problems, sorry."

    # If no specific conversational command is matched, return None
    return None