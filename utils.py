import requests
from bs4 import BeautifulSoup
import nltk
from nltk.tokenize import sent_tokenize
import re
from nltk.sentiment import SentimentIntensityAnalyzer
from gtts import gTTS
import os

def fetch_news(company_name):
    """
    Fetch news articles using NewsAPI instead of scraping Google News.
    """
    API_KEY = "cb986c0c1f754340953f93ad2823d2cc"  # 🔹 Replace with your actual API key
    url = f"https://newsapi.org/v2/everything?q={company_name}&apiKey={API_KEY}"

    response = requests.get(url)
    data = response.json()

    if data["status"] != "ok":
        return {"error": "Failed to fetch news."}

    news_data = []
    for article in data["articles"][:10]:  # Fetch first 10 articles
        news_data.append({
            "title": article["title"],
            "summary": article["description"] or "No summary available."
        })

    return news_data

nltk.download("vader_lexicon")
sia = SentimentIntensityAnalyzer()

def analyze_sentiment(text):
    """
    Performs sentiment analysis on the given text.
    """
    score = sia.polarity_scores(text)
    
    if score["compound"] >= 0.05:
        return "Positive"
    elif score["compound"] <= -0.05:
        return "Negative"
    else:
        return "Neutral"

def generate_tts(text, filename="output_hindi.mp3"):
    """
    Converts given text into Hindi speech and saves it as an MP3 file.
    """
    tts = gTTS(text=text, lang="hi")  # ✅ Set language to Hindi
    file_path = f"data/{filename}"
    tts.save(file_path)
    return file_path
