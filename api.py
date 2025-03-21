from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from utils import fetch_news, analyze_sentiment, generate_tts, extract_topics

app = FastAPI()

class TTSRequest(BaseModel):
    text: str

@app.get("/")
def read_root():
    return {"message": "Welcome to the News Summarization API!"}

@app.get("/fetch_news/")
def get_news(company: str):
    """Fetches news, analyzes sentiment, extracts topics, and generates comparative analysis."""
    news_articles = fetch_news(company)

    if "error" in news_articles:
        return {"error": "Failed to fetch news."}

    valid_articles = []
    sentiment_distribution = {"Positive": 0, "Negative": 0, "Neutral": 0}

    for article in news_articles:
        title = article.get("Title", "No Title Available").strip()
        summary = article.get("Summary", article.get("description", "No summary available.")).strip()

        if not title or not summary or title.lower() == "[removed]":
            continue  

        sentiment = analyze_sentiment(summary)
        topics = extract_topics(summary) or ["General News"]  

        sentiment_distribution[sentiment] += 1

        valid_articles.append({
            "Title": title,
            "Summary": summary,
            "Sentiment": sentiment,
            "Topics": topics
        })

    if not valid_articles:
        return {"error": "No valid news articles found."}

    # ✅ Ensure meaningful topic comparison
    comparisons = []
    for i in range(len(valid_articles) - 1):
        article1 = valid_articles[i]
        article2 = valid_articles[i + 1]

        comparison_text = f"Article {i+1} discusses **{article1['Title']}**, while Article {i+2} covers **{article2['Title']}**."

        if set(article1["Topics"]) & set(article2["Topics"]):  
            impact_text = "Both articles discuss similar themes, providing additional insights."
        else:
            impact_text = "The articles cover different aspects, offering a broader perspective."

        if article1["Sentiment"] == "Positive" and article2["Sentiment"] == "Negative":
            impact_text += " The first article is positive, but the second raises concerns."
        elif article1["Sentiment"] == "Negative" and article2["Sentiment"] == "Positive":
            impact_text += " The first article discusses risks, but the second brings positive developments."

        comparisons.append({"Comparison": comparison_text, "Impact": impact_text})

    # ✅ Handle topic overlaps
    if len(valid_articles) > 1:
        topics_1 = set(valid_articles[0]["Topics"])
        topics_2 = set(valid_articles[1]["Topics"])

        common_topics = topics_1 & topics_2 or {"Trending Topics"}
        unique_topics_1 = topics_1 - topics_2 or {"Miscellaneous Topics"}
        unique_topics_2 = topics_2 - topics_1 or {"Diverse Themes"}
    else:
        common_topics, unique_topics_1, unique_topics_2 = {"Only one article available"}, set(), set()

    comparative_sentiment = {
        "Sentiment Distribution": sentiment_distribution,
        "Coverage Differences": comparisons,
        "Topic Overlap": {
            "Common Topics": list(common_topics),
            "Unique Topics in Article 1": list(unique_topics_1),
            "Unique Topics in Article 2": list(unique_topics_2)
        }
    }
    
    final_sentiment = f"{company}’s latest news coverage is {'Mostly Positive' if sentiment_distribution['Positive'] > sentiment_distribution['Negative'] else 'Mostly Negative'}."
    
    # ✅ Generate Hindi TTS
    full_summary = " ".join([article["Summary"] for article in valid_articles])
    audio_file_path = generate_tts(full_summary, filename=f"{company}_analysis.mp3")

    return {
        "Company": company,
        "Articles": valid_articles,
        "Comparative Sentiment Score": comparative_sentiment,
        "Final Sentiment Analysis": final_sentiment,
        "Audio": audio_file_path
    }

@app.post("/generate_tts/")
def generate_hindi_tts(request: TTSRequest):
    """Generates Hindi TTS from the given text."""
    if not request.text.strip():
        raise HTTPException(status_code=400, detail="Text cannot be empty.")
    
    file_path = generate_tts(request.text)
    return {"audio_file": file_path}
