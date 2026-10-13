import requests
import nltk
from nltk.tokenize import sent_tokenize
import os
from nltk.sentiment import SentimentIntensityAnalyzer
from gtts import gTTS
from deep_translator import GoogleTranslator

# ✅ Download necessary NLTK data
nltk.download("vader_lexicon")
nltk.download("punkt")

# Initialize sentiment analyzer
sia = SentimentIntensityAnalyzer()

# ✅ Predefined topic keywords for dynamic topic extraction
TOPIC_KEYWORDS = {
    "Electric Vehicles": ["EV", "electric car", "Tesla", "battery"],
    "Stock Market": ["stock", "shares", "market", "finance"],
    "Innovation": ["innovation", "technology", "AI", "research"],
    "Regulations": ["regulation", "law", "policy", "government"],
    "Autonomous Vehicles": ["self-driving", "autonomous", "AI car"],
}

# ✅ News API Keys
API_KEYS = {
    "newsapi": "cb986c0c1f754340953f93ad2823d2cc",
    "nytimes": "FtgrqZy54Z0PaAXCgAn7G2AtvpiecKYE",
    "gnews": "b0ab6968b9bdde8af0bdb52032994905",
    "newsdata": "pub_7503037ddb9ba2d25d605f025845a066e9b7d",
    "mediastack": "56c650c7ffb4398f1a732891452ae32b",
}

def fetch_news(company_name):
    """
    Fetch news articles from multiple APIs and extract summaries.
    """
    news_sources = {
        "newsapi": f"https://newsapi.org/v2/everything?q={company_name}&apiKey={API_KEYS['newsapi']}",
        "nytimes": f"https://api.nytimes.com/svc/search/v2/articlesearch.json?q={company_name}&api-key={API_KEYS['nytimes']}",
        "gnews": f"https://gnews.io/api/v4/search?q={company_name}&token={API_KEYS['gnews']}",
        "newsdata": f"https://newsdata.io/api/1/news?apikey={API_KEYS['newsdata']}&q={company_name}",
        "mediastack": f"http://api.mediastack.com/v1/news?access_key={API_KEYS['mediastack']}&keywords={company_name}",
    }

    news_data = []

    for source, url in news_sources.items():
        try:
            response = requests.get(url)
            data = response.json()

            if "error" in data or not data:
                continue

            if source == "newsapi" and data.get("status") == "ok":
                articles = data.get("articles", [])[:10]  # Get first 10 articles
            elif source == "nytimes":
                articles = data.get("response", {}).get("docs", [])[:10]
            elif source in ["gnews", "newsdata", "mediastack"]:
                articles = data.get("articles", [])[:10]
            else:
                continue

            for article in articles:
                title = article.get("title", "").strip()
                summary = article.get("description", "").strip() or article.get("content", "").strip()

                if not title or not summary or title.lower() == "[removed]":
                    continue

                sentiment = analyze_sentiment(summary)
                topics = extract_topics(summary)

                news_data.append({
                    "Source": source,
                    "Title": title,
                    "Summary": summary,
                    "Sentiment": sentiment,
                    "Topics": topics
                })

        except Exception as e:
            print(f"Error fetching from {source}: {e}")

    if not news_data:
        return {"error": "No valid news articles found."}

    return news_data

def analyze_sentiment(text):
    """
    Perform sentiment analysis on the given text.
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
    Extract topics dynamically based on keyword matching.
    """
    extracted_topics = set()
    for topic, keywords in TOPIC_KEYWORDS.items():
        if any(keyword.lower() in text.lower() for keyword in keywords):
            extracted_topics.add(topic)
    return list(extracted_topics)

def generate_comparative_analysis(articles):
    """
    Generate a comparative analysis from extracted news articles.
    """
    sentiment_distribution = {"Positive": 0, "Negative": 0, "Neutral": 0}

    for article in articles:
        sentiment_distribution[article["Sentiment"]] += 1

    common_topics = set()
    unique_topics = {}

    if len(articles) > 1:
        common_topics = set(articles[0]["Topics"])
        for article in articles[1:]:
            common_topics &= set(article["Topics"])
        for i, article in enumerate(articles):
            unique_topics[f"Article {i+1}"] = set(article["Topics"]) - common_topics

    comparative_sentiment = {
        "Sentiment Distribution": sentiment_distribution,
        "Common Topics": list(common_topics),
        "Unique Topics": unique_topics
    }

    return comparative_sentiment

def generate_tts(text, filename="output_hindi.mp3", lang="hi"):
    """
    Convert given text into speech (Hindi by default, or specified language) and save it as an MP3 file.
    """
    save_dir = "data"
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)

    file_path = os.path.join(save_dir, filename)

    try:
        tts = gTTS(text=text, lang=lang)
        tts.save(file_path)
        try:
            print(f"✅ Audio saved: {file_path}")
        except UnicodeEncodeError:
            print(f"[OK] Audio saved: {file_path}")
        return file_path
    except Exception as e:
        try:
            print(f"❌ Error saving audio: {e}")
        except UnicodeEncodeError:
            print(f"[ERROR] Error saving audio: {e}")
        return None

def generate_full_summary(company_name):
    """
    Fetch news, perform sentiment analysis, generate comparative analysis, and create Hindi & Kannada TTS.
    """
    articles = fetch_news(company_name)

    if "error" in articles:
        return articles  # Return error message if API fails

    comparative_analysis = generate_comparative_analysis(articles)
    final_sentiment = f"{company_name}’s latest news coverage is {'Mostly Positive' if comparative_analysis['Sentiment Distribution']['Positive'] > comparative_analysis['Sentiment Distribution']['Negative'] else 'Mostly Negative'}."

    hindi_text = f"कंपनी {company_name} के समाचारों का विश्लेषण:\n\n"
    hindi_text += f"कुल {len(articles)} समाचार लेख मिले।\n\n"

    for i, article in enumerate(articles):
        hindi_text += f"🔹 लेख {i+1} ({article['Source']}): {article['Title']}।\n"
        hindi_text += f"📜 सारांश: {article['Summary']}।\n"
        hindi_text += f"📢 भावना: {article['Sentiment']}।\n\n"

    hindi_text += f"👉 समग्र भावना विश्लेषण:\n"
    hindi_text += f"✅ सकारात्मक लेख: {comparative_analysis['Sentiment Distribution']['Positive']}।\n"
    hindi_text += f"❌ नकारात्मक लेख: {comparative_analysis['Sentiment Distribution']['Negative']}।\n"
    hindi_text += f"⚖ तटस्थ लेख: {comparative_analysis['Sentiment Distribution']['Neutral']}।\n"

    try:
        translated_text = GoogleTranslator(source="auto", target="hi").translate(hindi_text)
    except Exception as e:
        print(f"Hindi translation failed: {e}")
        translated_text = "अनुवाद उपलब्ध नहीं है।"

    audio_path = generate_tts(translated_text, f"{company_name}_analysis.mp3", lang="hi")

    try:
        translated_kannada_text = GoogleTranslator(source="auto", target="kn").translate(hindi_text)
    except Exception as e:
        print(f"Kannada translation failed: {e}")
        translated_kannada_text = "ಅನುವಾದ ಲಭ್ಯವಿಲ್ಲ."

    audio_kannada_path = generate_tts(translated_kannada_text, f"{company_name}_analysis_kannada.mp3", lang="kn")

    return {
        "Company": company_name,
        "Articles": articles,
        "Comparative Analysis": comparative_analysis,
        "Final Sentiment Analysis": final_sentiment,
        "Audio": audio_path,
        "Audio_Kannada": audio_kannada_path
    }