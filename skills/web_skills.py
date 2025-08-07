import wikipedia
import pywhatkit
import webbrowser
import requests
from bs4 import BeautifulSoup
import yfinance as yf
import translators as ts
from skills.memory_skills import get_preference

# --- News Skill Enhancement ---
NEWS_SOURCES = {
    "bbc": {"url": "https://www.bbc.com/news", "tag": "h3"},
    "reuters": {"url": "https://www.reuters.com/", "tag": "h3"},
    "ap": {"url": "https://apnews.com/hub/ap-top-news", "tag": "h3"}
}

def get_news_headlines():
    """Fetches top news headlines from a preferred or default source."""
    preferred_source_name = get_preference("news_source") or "bbc"
    source = NEWS_SOURCES.get(preferred_source_name.lower())

    if not source:
        return f"I don't recognize {preferred_source_name} as a news source. My available sources are BBC, Reuters, and AP."

    try:
        response = requests.get(source["url"])
        soup = BeautifulSoup(response.text, 'html.parser')
        headlines = soup.find_all(source["tag"])
            
        news_summary = f"Here are the top headlines from {preferred_source_name.upper()}. "
        count = 0
        for h in headlines:
            text = h.get_text().strip()
            # Filter out empty or non-headline tags
            if len(text.split()) > 3:
                news_summary += f"{text}. "
                count += 1
                if count >= 4: # Read out top 4
                    break
        return news_summary
    except Exception as e:
        print(f"News Skill Error: {e}")
        return "Sorry, I'm having trouble fetching the news right now."

# --- Other skills remain the same ---
def search_wikipedia(command):
    """Searches Wikipedia for a query."""
    query = command.replace("wikipedia", "").replace("search", "").strip()
    try:
        results = wikipedia.summary(query, sentences=2)
        return f"According to Wikipedia... {results}"
    except Exception:
        return f"Sorry, I could not find any results for {query} on Wikipedia."

def play_on_youtube(command):
    """Searches for and plays a video on YouTube."""
    search_term = command.replace("play", "").replace("on youtube", "").strip()
    pywhatkit.playonyt(search_term)
    return f"Playing {search_term} on YouTube."

def search_web(command):
    """Searches the web for a query."""
    query = command.replace("search for", "").replace("search", "").strip()
    pywhatkit.search(query)
    return f"Searching for {query} on the web."

def get_stock_price(command):
    """Gets the stock price for a given ticker symbol."""
    try:
        words = command.split()
        for i, word in enumerate(words):
            if word.lower() == 'of' and i + 1 < len(words):
                ticker_symbol = words[i+1].upper()
                break
        else:
            return "I couldn't identify the stock ticker. Please phrase it as 'price of [ticker]'."
        stock = yf.Ticker(ticker_symbol)
        todays_data = stock.history(period='1d')
        if todays_data.empty:
            return f"I couldn't find any data for the stock ticker {ticker_symbol}."
        price = todays_data['Close'][0]
        return f"The current price of {ticker_symbol} is ${price:.2f}."
    except Exception as e:
        print(f"Stock Skill Error: {e}")
        return "I had trouble fetching the stock price."

def translate_text(command):
    """Translates text to a specified language."""
    try:
        parts = command.lower().split(' to ')
        target_language = parts[-1].strip()
        text_to_translate = parts[0].replace('translate', '').strip().strip("'\"")
        translated_text = ts.translate_text(text_to_translate, to_language=target_language)
        return f"'{text_to_translate}' in {target_language} is '{translated_text}'."
    except Exception as e:
        print(f"Translate Skill Error: {e}")
        return "I had trouble with the translation. Please check the language or try again."

def get_directions(command):
    """Opens Google Maps with directions to a location."""
    destination = command.replace("directions to", "").strip()
    maps_url = f"https://www.google.com/maps/dir/?api=1&destination={destination.replace(' ', '+')}"
    webbrowser.open(maps_url)
    return f"Opening Google Maps with directions to {destination}."