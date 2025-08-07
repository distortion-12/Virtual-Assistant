from PIL import ImageGrab
import google.generativeai as genai
import config

# Use the Gemini 1.5 Pro model which supports vision
try:
    genai.configure(api_key=config.GEMINI_API_KEY)
    vision_model = genai.GenerativeModel('gemini-1.5-pro-latest')
except Exception as e:
    print(f"Error configuring Vision model: {e}")
    vision_model = None

def analyze_screen(prompt: str) -> str:
    """Takes a screenshot and uses Gemini Pro Vision to analyze it."""
    if not vision_model:
        return "The vision AI model is not configured correctly."

    try:
        # Take a screenshot
        screenshot = ImageGrab.grab()
        
        # Remove the wake word from the prompt for a cleaner query
        clean_prompt = prompt.replace("lyra", "").strip()

        # Ask the model to analyze the image with the user's prompt
        response = vision_model.generate_content([clean_prompt, screenshot])
        
        return response.text
    except Exception as e:
        print(f"Vision Skill Error: {e}")
        return "I'm having trouble analyzing the screen right now."