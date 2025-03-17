import streamlit as st
import requests
from googletrans import Translator  # ✅ Install with: pip install googletrans==4.0.0-rc1

translator = Translator()

st.title("📢 News Summarization & Sentiment Analysis")
st.sidebar.header("🔍 Enter a Company Name")

company_name = st.sidebar.text_input("Company Name", "Tesla")

if st.sidebar.button("Fetch News"):
    response = requests.get(f"http://127.0.0.1:8000/fetch_news/?company={company_name}")

    if response.status_code == 200:
        data = response.json()
        st.write(f"### News for {data['company']}")

        full_summary = ""

        for article in data["articles"]:
            st.subheader(article["title"])
            st.write(article["summary"])
            st.write(f"**🟢 Sentiment:** {article['sentiment']}")
            full_summary += article["summary"] + " "

        # ✅ Translate to Hindi before sending to TTS
        translated_text = translator.translate(full_summary, dest="hi").text

        # ✅ Generate Hindi Audio Summary
        tts_response = requests.get(f"http://127.0.0.1:8000/generate_tts/?text={translated_text}")

        if tts_response.status_code == 200:
            audio_file = tts_response.json()["audio_file"]
            st.audio(audio_file, format="audio/mp3")

    else:
        st.error("❌ Failed to fetch news!")
