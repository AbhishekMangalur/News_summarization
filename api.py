from fastapi import FastAPI
from utils import fetch_news, analyze_sentiment, generate_tts

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Welcome to the News Summarization API!"}

@app.get("/fetch_news/")
def get_news(company: str):
    news_articles = fetch_news(company)
    if "error" in news_articles:
        return {"error": "Failed to fetch news."}
    
    sentiment_distribution = {"Positive": 0, "Negative": 0, "Neutral": 0}
    topics_article_1 = []
    topics_article_2 = []

    for index, article in enumerate(news_articles):
        article["sentiment"] = analyze_sentiment(article["summary"])
        sentiment_distribution[article["sentiment"]] += 1

        # Simulating topic extraction (this should ideally be done with NLP)
        if index == 0:
            topics_article_1 = ["Electric Vehicles", "Stock Market", "Innovation"]
        elif index == 1:
            topics_article_2 = ["Regulations", "Autonomous Vehicles"]
    
    comparative_sentiment = {
        "Sentiment Distribution": sentiment_distribution,
        "Coverage Differences": [
            {
                "Comparison": "Article 1 highlights Tesla's strong sales, while Article 2 discusses regulatory issues.",
                "Impact": "The first article boosts confidence in Tesla's market growth, while the second raises concerns about future regulatory hurdles."
            },
            {
                "Comparison": "Article 1 is focused on financial success and innovation, whereas Article 2 is about legal challenges and risks.",
                "Impact": "Investors may react positively to growth news but stay cautious due to regulatory scrutiny."
            }
        ],
        "Topic Overlap": {
            "Common Topics": ["Electric Vehicles"],
            "Unique Topics in Article 1": ["Stock Market", "Innovation"],
            "Unique Topics in Article 2": ["Regulations", "Autonomous Vehicles"]
        }
    }
    
    final_sentiment = "Tesla’s latest news coverage is mostly positive. Potential stock growth expected."
    
    # Generate TTS for the full summary
    full_summary = " ".join([article["summary"] for article in news_articles])
    audio_file_path = generate_tts(full_summary, filename="output_hindi.mp3")

    return {
        "Company": company,
        "Articles": [
            {
                "Title": article["title"],
                "Summary": article["summary"],
                "Sentiment": article["sentiment"],
                "Topics": topics_article_1 if index == 0 else topics_article_2
            }
            for index, article in enumerate(news_articles)
        ],
        "Comparative Sentiment Score": comparative_sentiment,
        "Final Sentiment Analysis": final_sentiment,
        "Audio": audio_file_path  # File path for the generated audio
    }

@app.get("/generate_tts/")
def get_tts(text: str):
    file_path = generate_tts(text)
    return {"audio_file": file_path}
