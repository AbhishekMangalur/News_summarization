import os
import streamlit as st
import requests
import inspect
import asyncio
import concurrent.futures
from googletrans import Translator
from api import get_news
from utils import generate_tts

translator = Translator()

def translate_text(text, dest):
    """Safely translate text, supporting both sync (4.0.0-rc1) and async (4.0.2+) googletrans with deep_translator fallback."""
    if not text or not text.strip():
        return ""
    try:
        res = translator.translate(text, dest=dest)
        if inspect.isawaitable(res):
            try:
                loop = asyncio.get_running_loop()
            except RuntimeError:
                loop = None
            if loop and loop.is_running():
                with concurrent.futures.ThreadPoolExecutor() as pool:
                    res = pool.submit(lambda: asyncio.run(translator.translate(text, dest=dest))).result()
            else:
                res = asyncio.run(res)
        if hasattr(res, "text") and res.text:
            return res.text
    except Exception:
        pass

    try:
        from deep_translator import GoogleTranslator
        return GoogleTranslator(source="auto", target=dest).translate(text)
    except Exception:
        return text

def fetch_news_data(company_name, backend_url=""):
    """
    Fetch news data either from a FastAPI backend (if configured and responding with JSON)
    or directly via Python function calls.
    """
    if backend_url:
        cleaned_url = backend_url.rstrip("/")
        try:
            endpoint = f"{cleaned_url}/fetch_news/?company={company_name}"
            response = requests.get(endpoint, timeout=30, headers={"Accept": "application/json"})
            content_type = response.headers.get("content-type", "")

            if response.status_code == 200 and "application/json" in content_type:
                return response.json()
            elif "text/html" in content_type:
                st.warning(
                    "⚠️ The configured Backend URL returned HTML instead of JSON. "
                    "(This happens when pointing to the Streamlit UI rather than FastAPI.) "
                    "Running analysis directly."
                )
            else:
                st.warning(f"⚠️ Backend returned status {response.status_code}. Running analysis directly.")
        except Exception as e:
            st.warning(f"⚠️ Could not reach backend API at {cleaned_url} ({e}). Running analysis directly.")

    # Direct local execution
    return get_news(company_name)

def generate_tts_audio(text, lang="hi", filename=None, backend_url=""):
    """Generate TTS audio via backend API if available, or directly via utils.generate_tts."""
    if backend_url:
        cleaned_url = backend_url.rstrip("/")
        try:
            payload = {"text": text, "lang": lang}
            if filename:
                payload["filename"] = filename
            endpoint = f"{cleaned_url}/generate_tts/"
            response = requests.post(endpoint, json=payload, timeout=30, headers={"Accept": "application/json"})
            content_type = response.headers.get("content-type", "")

            if response.status_code == 200 and "application/json" in content_type:
                audio_path = response.json().get("audio_file")
                if audio_path and os.path.exists(audio_path):
                    return audio_path
        except Exception:
            pass

    # Direct local execution
    target_filename = filename or (f"output_{lang}.mp3" if lang != "hi" else "output_hindi.mp3")
    return generate_tts(text, filename=target_filename, lang=lang)

st.title("📢 News Summarization & Sentiment Analysis")
st.sidebar.header("🔍 Enter a Company Name")

company_name = st.sidebar.text_input("Company Name", "Tesla").strip()

with st.sidebar.expander("⚙️ Advanced Settings", expanded=False):
    backend_url = st.text_input(
        "Backend API URL (Optional)",
        value=os.environ.get("BACKEND_URL", ""),
        help="Leave blank to run directly in Streamlit. If you deployed FastAPI separately, enter its URL here (e.g. http://127.0.0.1:8000)."
    ).strip()

if st.sidebar.button("Fetch News"):
    if not company_name:
        st.warning("Please enter a company name.")
        st.stop()

    with st.spinner(f"Fetching and analyzing news for {company_name}..."):
        data = fetch_news_data(company_name, backend_url=backend_url)

    if not data or "error" in data:
        st.error(f"❌ {data.get('error', 'Failed to fetch news.') if data else 'Failed to fetch news.'}")
    else:
        st.write(f"### News for {data.get('Company', company_name)}")

        articles = data.get("Articles", [])
        full_summary = ""

        for article in articles:
            title = article.get("Title", "No Title Available")
            summary = article.get("Summary", "No summary available.")
            sentiment = article.get("Sentiment", "Unknown")
            topics = article.get("Topics", ["General News"])

            st.subheader(title)
            st.write(summary)
            st.write(f"**🟢 Sentiment:** {sentiment}")

            if topics:
                st.write(f"**📌 Topics:** {', '.join(topics)}")

            full_summary += summary + " "

        # ✅ Display Sentiment Distribution
        st.write("### 📊 Sentiment Distribution")
        comp_score = data.get("Comparative Sentiment Score", {})
        sentiment_dist = comp_score.get("Sentiment Distribution", {"Positive": 0, "Negative": 0, "Neutral": 0})
        st.write(
            f"**Positive:** {sentiment_dist.get('Positive', 0)} | "
            f"**Negative:** {sentiment_dist.get('Negative', 0)} | "
            f"**Neutral:** {sentiment_dist.get('Neutral', 0)}"
        )

        # ✅ Display Coverage Differences
        st.write("### ⚖️ Coverage Differences")
        coverage_diffs = comp_score.get("Coverage Differences", [])
        if coverage_diffs:
            for diff in coverage_diffs:
                st.write(f"**🆚 Comparison:** {diff.get('Comparison', '')}")
                st.write(f"**📉 Impact:** {diff.get('Impact', '')}")
                st.markdown("---")
        else:
            st.write("No coverage differences available.")

        # ✅ Display Topic Overlap
        st.write("### 🔍 Topic Overlap")
        topic_overlap = comp_score.get("Topic Overlap", {})

        common_topics = topic_overlap.get("Common Topics", ["Trending Topics"])
        unique_1 = topic_overlap.get("Unique Topics in Article 1", ["Miscellaneous Topics"])
        unique_2 = topic_overlap.get("Unique Topics in Article 2", ["Diverse Themes"])

        st.write(f"**Common Topics:** {', '.join(common_topics)}")
        st.write(f"**Unique in Article 1:** {', '.join(unique_1)}")
        st.write(f"**Unique in Article 2:** {', '.join(unique_2)}")

        # ✅ Translate full summary to Hindi and generate Audio
        if full_summary.strip():
            try:
                with st.spinner("Generating Hindi audio summary..."):
                    translated_text = translate_text(full_summary, dest="hi")
                    audio_file = generate_tts_audio(
                        translated_text,
                        lang="hi",
                        filename=f"{company_name}_hindi.mp3",
                        backend_url=backend_url
                    )

                    if audio_file and os.path.exists(audio_file):
                        st.write("### 🔊 Listen to Summary in Hindi")
                        st.audio(audio_file, format="audio/mp3")
                    else:
                        st.warning("Could not generate Hindi audio.")
            except Exception as e:
                st.error(f"❌ Failed to generate Hindi audio summary: {e}")

            # ✅ Translate full summary to Kannada and generate Audio
            try:
                with st.spinner("Generating Kannada audio summary..."):
                    translated_kannada_text = translate_text(full_summary, dest="kn")
                    kannada_audio_file = generate_tts_audio(
                        translated_kannada_text,
                        lang="kn",
                        filename=f"{company_name}_kannada.mp3",
                        backend_url=backend_url
                    )

                    if kannada_audio_file and os.path.exists(kannada_audio_file):
                        st.write("### 🔊 Listen to Summary in Kannada")
                        st.audio(kannada_audio_file, format="audio/mp3")
                    else:
                        st.warning("Could not generate Kannada audio.")
            except Exception as e:
                st.error(f"❌ Failed to generate Kannada audio summary: {e}")

        # ✅ Display Final Sentiment Analysis
        st.write("### 🔥 Final Sentiment Analysis")
        st.write(f"**{data.get('Final Sentiment Analysis', 'N/A')}**")