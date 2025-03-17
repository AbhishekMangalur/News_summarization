import requests
import nltk
from nltk.tokenize import sent_tokenize
import os
from nltk.sentiment import SentimentIntensityAnalyzer
from gtts import gTTS

# ✅ Download necessary NLTK data
nltk.download("vader_lexicon")
nltk.download("punkt")

# Initialize sentiment analyzer
sia = SentimentIntensityAnalyzer()

# Predefined topic keywords for dynamic topic extraction
TOPIC_KEYWORDS = {
    "Electric Vehicles": ["EV", "electric car", "Tesla", "battery"],
    "Stock Market": ["stock", "shares", "market", "finance"],
    "Innovation": ["innovation", "technology", "AI", "research"],
    "Regulations": ["regulation", "law", "policy", "government"],
    "Autonomous Vehicles": ["self-driving", "autonomous", "AI car"],
}

def fetch_news(company_name):
    """
    Fetch news articles using NewsAPI and extract summaries.
    """
    API_KEY = "cb986c0c1f754340953f93ad2823d2cc"  # Replace with your actual API key
    url = f"https://newsapi.org/v2/everything?q={company_name}&apiKey={API_KEY}"

    response = requests.get(url)
    data = response.json()

    if "status" not in data or data["status"] != "ok":
        return {"error": "Failed to fetch news."}

    news_data = []
    for article in data.get("articles", [])[:10]:  # Fetch first 10 articles
        title = article.get("title", "").strip()
        summary = article.get("description", "").strip() or article.get("content", "").strip()

        # ✅ Skip articles with missing or invalid content
        if not title or not summary or title.lower() == "[removed]":
            continue

        sentiment = analyze_sentiment(summary)
        topics = extract_topics(summary)

        news_data.append({
            "Title": title,
            "Summary": summary,
            "Sentiment": sentiment,
            "Topics": topics
        })

    if not news_data:
        return {"error": "No valid news articles found."}

    return news_data

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

def extract_topics(text):
    """
    Extracts topics dynamically based on keyword matching.
    """
    extracted_topics = set()
    for topic, keywords in TOPIC_KEYWORDS.items():
        if any(keyword.lower() in text.lower() for keyword in keywords):
            extracted_topics.add(topic)
    return list(extracted_topics)

def generate_comparative_analysis(articles):
    """
    Generates a comparative analysis from extracted news articles.
    """
    sentiment_distribution = {"Positive": 0, "Negative": 0, "Neutral": 0}

    for article in articles:
        sentiment_distribution[article["Sentiment"]] += 1

    # Extract topic overlaps
    if len(articles) > 1:
        common_topics = set(articles[0]["Topics"]) & set(articles[1]["Topics"])
        unique_topics_1 = set(articles[0]["Topics"]) - set(articles[1]["Topics"])
        unique_topics_2 = set(articles[1]["Topics"]) - set(articles[0]["Topics"])
    else:
        common_topics, unique_topics_1, unique_topics_2 = set(), set(), set()

    comparative_sentiment = {
        "Sentiment Distribution": sentiment_distribution,
        "Coverage Differences": [
            {
                "Comparison": f"Article 1 discusses {articles[0]['Title']}, while Article 2 focuses on {articles[1]['Title']}." if len(articles) > 1 else "Only one article available.",
                "Impact": "The first article highlights business growth, while the second raises challenges." if len(articles) > 1 else "No comparative analysis possible."
            }
        ],
        "Topic Overlap": {
            "Common Topics": list(common_topics),
            "Unique Topics in Article 1": list(unique_topics_1),
            "Unique Topics in Article 2": list(unique_topics_2)
        }
    }

    return comparative_sentiment

def generate_tts(text, filename="output_hindi.mp3"):
    """
    Converts given text into Hindi speech and saves it as an MP3 file.
    """
    # Ensure the 'data/' directory exists
    save_dir = "data"
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)

    file_path = os.path.join(save_dir, filename)

    try:
        tts = gTTS(text=text, lang="hi")  # ✅ Generate Hindi speech
        tts.save(file_path)
        print(f"✅ Audio saved: {file_path}")
        return file_path
    except Exception as e:
        print(f"❌ Error saving audio: {e}")
        return None

def generate_full_summary(company_name):
    """
    Fetches news, performs sentiment analysis, generates comparative analysis, and creates Hindi TTS.
    """
    articles = fetch_news(company_name)

    if "error" in articles:
        return articles  # Return error message if API fails

    comparative_analysis = generate_comparative_analysis(articles)
    final_sentiment = f"{company_name}’s latest news coverage is {'Mostly Positive' if comparative_analysis['Sentiment Distribution']['Positive'] > comparative_analysis['Sentiment Distribution']['Negative'] else 'Mostly Negative'}."

    # ✅ Generate Hindi speech text
    hindi_text = f"कंपनी {company_name} के समाचारों का विश्लेषण:\n\n"
    hindi_text += f"कुल {len(articles)} समाचार लेख मिले।\n\n"

    for i, article in enumerate(articles):
        hindi_text += f"🔹 लेख {i+1}: {article['Title']}।\n"
        hindi_text += f"📜 सारांश: {article['Summary']}।\n"
        hindi_text += f"📢 भावना: {article['Sentiment']}।\n\n"

    hindi_text += f"👉 समग्र भावना विश्लेषण:\n"
    hindi_text += f"✅ सकारात्मक लेख: {comparative_analysis['Sentiment Distribution']['Positive']}।\n"
    hindi_text += f"❌ नकारात्मक लेख: {comparative_analysis['Sentiment Distribution']['Negative']}।\n"
    hindi_text += f"⚖ तटस्थ लेख: {comparative_analysis['Sentiment Distribution']['Neutral']}।\n"

    # ✅ Generate and return Hindi TTS
    audio_path = generate_tts(hindi_text, f"{company_name}_analysis.mp3")

    return {
        "Company": company_name,
        "Articles": articles,
        "Comparative Sentiment Score": comparative_analysis,
        "Final Sentiment Analysis": final_sentiment,
        "Audio": audio_path
    }
