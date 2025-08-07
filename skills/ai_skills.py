import google.generativeai as genai
import config
# We don't need speak here anymore

try:
    genai.configure(api_key=config.GEMINI_API_KEY)
    model = genai.GenerativeModel('gemini-1.5-flash')
except Exception as e:
    print(f"Error configuring Gemini: {e}")
    model = None

def get_gemini_response(query: str):
    """Gets a direct answer from the Gemini model."""
    if not model:
        return "The AI model is not configured correctly. Please check your API key."

    try:
        prompt = f"You are a helpful AI assistant. Answer the following query directly and concisely: {query}"
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        print(f"Gemini API Error: {e}")
        return "I'm having trouble connecting to my knowledge base right now."