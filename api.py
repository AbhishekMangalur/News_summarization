from fastapi import FastAPI
from utils import fetch_news, analyze_sentiment, generate_tts

app = FastAPI()

# ✅ Add a root endpoint to prevent 404 error
@app.get("/")
def read_root():
    return {"message": "Welcome to the News Summarization API!"}

@app.get("/fetch_news/")
def get_news(company: str):
    news_articles = fetch_news(company)
    if "error" in news_articles:
        return {"error": "Failed to fetch news."}
    
    for article in news_articles:
        article["sentiment"] = analyze_sentiment(article["summary"])

    return {"company": company, "articles": news_articles}

@app.get("/generate_tts/")
def get_tts(text: str):
    file_path = generate_tts(text)
    return {"audio_file": file_path}
