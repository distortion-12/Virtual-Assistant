import json
import os
import google.generativeai as genai
import config

MEMORY_FILE = 'memory.json'
memory_model = None

# Configure the Gemini model for memory processing
try:
    genai.configure(api_key=config.GEMINI_API_KEY)
    memory_model = genai.GenerativeModel('gemini-1.5-flash')
except Exception as e:
    print(f"Error configuring Gemini for memory: {e}")

def load_memory():
    """Loads the memory from the JSON file."""
    if not os.path.exists(MEMORY_FILE):
        return {"facts": {}, "preferences": {}}
    try:
        with open(MEMORY_FILE, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"facts": {}, "preferences": {}}

def save_memory(data):
    """Saves the memory to the JSON file."""
    with open(MEMORY_FILE, 'w') as f:
        json.dump(data, f, indent=4)

# --- New Preference Management Functions ---

def get_preference(key):
    """Gets a specific preference from memory."""
    memory = load_memory()
    return memory.get("preferences", {}).get(key)

def set_preference(key, value):
    """Saves a specific preference to memory."""
    memory = load_memory()
    if "preferences" not in memory:
        memory["preferences"] = {}
    memory["preferences"][key] = value
    save_memory(memory)
    print(f"Preference Saved: {key} = {value}")

# --- Existing Fact Memory Functions (Slightly modified) ---

def remember_contextually(command: str) -> str:
    """Uses AI to understand and save a key fact to memory's 'facts' section."""
    if not memory_model:
        return "My memory circuits are not configured correctly. Please check the API key."
    
    # AI prompt to extract a key-value fact
    prompt = f"""
    Analyze the following user command and extract the key piece of information to be remembered as a fact.
    Return the information as a simple JSON object with a "key" and a "value".
    For example, if the user says 'remember my anniversary is on March 15th', you should return:
    {{"key": "my anniversary", "value": "March 15th"}}
    
    User command: "{command}"
    """
    
    try:
        response = memory_model.generate_content(prompt)
        json_response_str = response.text.strip().replace("```json", "").replace("```", "")
        data_to_remember = json.loads(json_response_str)
        key = data_to_remember.get("key")
        value = data_to_remember.get("value")

        if key and value:
            memory = load_memory()
            memory["facts"][key] = value
            save_memory(memory)
            return f"Understood. I'll remember that {key} is {value}."
        else:
            return "I understood you wanted me to remember something, but I couldn't quite grasp the specific detail."
    except Exception as e:
        print(f"Contextual Memory Error: {e}")
        return "I had a little trouble processing that memory. Could you try phrasing it differently?"


def recall_info(command: str) -> str:
    """Recalls a fact from memory's 'facts' section."""
    try:
        keywords = ["what is ", "what's ", "what do you know about ", "what did I tell you about "]
        key_to_find = None
        for word in keywords:
            if word in command:
                key_to_find = command.split(word)[1].strip().replace("?","")
                break
        
        if key_to_find:
            memory = load_memory()
            value = memory.get("facts", {}).get(key_to_find)
            if value:
                return f"Based on my memory, {key_to_find} is {value}."
            else:
                return f"I don't seem to have a memory about '{key_to_find}'."
    except Exception as e:
        print(f"Error in recall_info: {e}")
        return "I had trouble accessing my memory."
        
    return "What would you like to know about?"