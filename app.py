import streamlit as st
import requests
import inspect
import asyncio
import concurrent.futures
from googletrans import Translator

# Your deployed FastAPI backend URL
BACKEND_URL = "https://news-summarization-wrk4.onrender.com"

translator = Translator()


def translate_text(text, dest):
    """Translate text using googletrans."""
    res = translator.translate(text, dest=dest)

    if inspect.isawaitable(res):
        try:
            asyncio.get_running_loop()
        except RuntimeError:
            res = asyncio.run(res)
        else:
            # Run the coroutine in a separate thread if a loop is active
            def run_translation():
                async def translate():
                    async with Translator() as async_translator:
                        return await async_translator.translate(
                            text, dest=dest
                        )
                return asyncio.run(translate())

            with concurrent.futures.ThreadPoolExecutor() as pool:
                res = pool.submit(run_translation).result()

    return res.text


st.title("📢 News Summarization & Sentiment Analysis")
st.sidebar.header("🔍 Enter a Company Name")

company_name = st.sidebar.text_input("Company Name", "Tesla")

if st.sidebar.button("Fetch News"):
    try:
        with st.spinner("Fetching news..."):
            response = requests.get(
                f"{BACKEND_URL}/fetch_news/",
                params={"company": company_name},
                timeout=120,
            )
            response.raise_for_status()
            data = response.json()

        if "error" in data:
            st.error(f"❌ {data['error']}")
            st.stop()

        st.write(f"### News for {data['Company']}")

        full_summary = ""

        for article in data["Articles"]:
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

        # Sentiment Distribution
        st.write("### 📊 Sentiment Distribution")
        sentiment_dist = data["Comparative Sentiment Score"]["Sentiment Distribution"]

        st.write(
            f"**Positive:** {sentiment_dist['Positive']} | "
            f"**Negative:** {sentiment_dist['Negative']} | "
            f"**Neutral:** {sentiment_dist['Neutral']}"
        )

        # Coverage Differences
        st.write("### ⚖️ Coverage Differences")

        for diff in data["Comparative Sentiment Score"]["Coverage Differences"]:
            st.write(f"**🆚 Comparison:** {diff['Comparison']}")
            st.write(f"**📉 Impact:** {diff['Impact']}")
            st.markdown("---")

        # Topic Overlap
        st.write("### 🔍 Topic Overlap")
        topic_overlap = data["Comparative Sentiment Score"]["Topic Overlap"]

        common_topics = topic_overlap.get("Common Topics", ["Trending Topics"])
        unique_1 = topic_overlap.get("Unique Topics in Article 1", ["Miscellaneous Topics"])
        unique_2 = topic_overlap.get("Unique Topics in Article 2", ["Diverse Themes"])

        st.write(f"**Common Topics:** {', '.join(common_topics)}")
        st.write(f"**Unique in Article 1:** {', '.join(unique_1)}")
        st.write(f"**Unique in Article 2:** {', '.join(unique_2)}")

        # Hindi Audio Summary
        try:
            with st.spinner("Generating Hindi audio summary..."):
                hindi_text = translate_text(full_summary, dest="hi")

                tts_response = requests.post(
                    f"{BACKEND_URL}/generate_tts/",
                    json={"text": hindi_text, "lang": "hi"},
                    timeout=120,
                )
                tts_response.raise_for_status()

                audio_file = tts_response.json()["audio_file"]

                st.write("### 🔊 Listen to Summary in Hindi")
                st.audio(audio_file, format="audio/mp3")

        except Exception as e:
            st.error(f"❌ Failed to generate Hindi audio summary: {e}")

        # Kannada Audio Summary
        try:
            with st.spinner("Generating Kannada audio summary..."):
                kannada_text = translate_text(full_summary, dest="kn")

                tts_kannada_response = requests.post(
                    f"{BACKEND_URL}/generate_tts/",
                    json={
                        "text": kannada_text,
                        "lang": "kn",
                        "filename": "output_kannada.mp3",
                    },
                    timeout=120,
                )
                tts_kannada_response.raise_for_status()

                kannada_audio_file = tts_kannada_response.json()["audio_file"]

                st.write("### 🔊 Listen to Summary in Kannada")
                st.audio(kannada_audio_file, format="audio/mp3")

        except Exception as e:
            st.error(f"❌ Failed to generate Kannada audio summary: {e}")

        # Final Sentiment Analysis
        st.write("### 🔥 Final Sentiment Analysis")
        st.write(f"**{data['Final Sentiment Analysis']}**")

    except requests.exceptions.RequestException as e:
        st.error(f"❌ Backend request failed: {e}")
    except (ValueError, KeyError) as e:
        st.error(f"❌ Invalid response from backend: {e}")
