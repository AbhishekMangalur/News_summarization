import streamlit as st
import requests
from googletrans import Translator

translator = Translator()

st.title("📢 News Summarization & Sentiment Analysis")
st.sidebar.header("🔍 Enter a Company Name")

company_name = st.sidebar.text_input("Company Name", "Tesla")

if st.sidebar.button("Fetch News"):
    response = requests.get(f"http://127.0.0.1:8000/fetch_news/?company={company_name}")

    if response.status_code == 200:
        data = response.json()
        st.write(f"### News for {data['Company']}")

        full_summary = ""

        for article in data["Articles"]:
            st.subheader(article["Title"])
            st.write(article["Summary"])
            st.write(f"**🟢 Sentiment:** {article['Sentiment']}")
            st.write(f"**📌 Topics:** {', '.join(article['Topics'])}")
            full_summary += article["Summary"] + " "

        # ✅ Display Sentiment Distribution
        st.write("### 📊 Sentiment Distribution")
        sentiment_dist = data["Comparative Sentiment Score"]["Sentiment Distribution"]
        st.write(f"**Positive:** {sentiment_dist['Positive']} | **Negative:** {sentiment_dist['Negative']} | **Neutral:** {sentiment_dist['Neutral']}")

        # ✅ Display Coverage Differences
        st.write("### ⚖️ Coverage Differences")
        for diff in data["Comparative Sentiment Score"]["Coverage Differences"]:
            st.write(f"**🆚 Comparison:** {diff['Comparison']}")
            st.write(f"**📉 Impact:** {diff['Impact']}")
            st.markdown("---")

        # ✅ Display Topic Overlap
        st.write("### 🔍 Topic Overlap")
        topic_overlap = data["Comparative Sentiment Score"]["Topic Overlap"]
        st.write(f"**Common Topics:** {', '.join(topic_overlap['Common Topics'])}")
        st.write(f"**Unique in Article 1:** {', '.join(topic_overlap['Unique Topics in Article 1'])}")
        st.write(f"**Unique in Article 2:** {', '.join(topic_overlap['Unique Topics in Article 2'])}")

        # ✅ Translate to Hindi before sending to TTS
        translated_text = translator.translate(full_summary, dest="hi").text

        # ✅ Generate Hindi Audio Summary
        tts_response = requests.get(f"http://127.0.0.1:8000/generate_tts/?text={translated_text}")

        if tts_response.status_code == 200:
            audio_file = tts_response.json()["audio_file"]
            st.audio(audio_file, format="audio/mp3")

        # ✅ Display Final Sentiment Analysis
        st.write("### 🔥 Final Sentiment Analysis")
        st.write(f"**{data['Final Sentiment Analysis']}**")

    else:
        st.error("❌ Failed to fetch news!")
