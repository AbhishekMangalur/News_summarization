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

        if "error" in data:
            st.error(f"❌ {data['error']}")
        else:
            st.write(f"### News for {data['Company']}")

            full_summary = ""

            for article in data["Articles"]:
                title = article.get("Title", "No Title Available")
                summary = article.get("Summary", "No summary available.")
                sentiment = article.get("Sentiment", "Unknown")
                topics = article.get("Topics", ["General News"])  # ✅ Ensures topics are always present

                st.subheader(title)
                st.write(summary)
                st.write(f"**🟢 Sentiment:** {sentiment}")

                if topics:
                    st.write(f"**📌 Topics:** {', '.join(topics)}")

                full_summary += summary + " "

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

            # ✅ Display Topic Overlap (Now handles empty cases properly)
            st.write("### 🔍 Topic Overlap")
            topic_overlap = data["Comparative Sentiment Score"]["Topic Overlap"]

            common_topics = topic_overlap.get("Common Topics", ["Trending Topics"])
            unique_1 = topic_overlap.get("Unique Topics in Article 1", ["Miscellaneous Topics"])
            unique_2 = topic_overlap.get("Unique Topics in Article 2", ["Diverse Themes"])

            st.write(f"**Common Topics:** {', '.join(common_topics)}")
            st.write(f"**Unique in Article 1:** {', '.join(unique_1)}")
            st.write(f"**Unique in Article 2:** {', '.join(unique_2)}")

            # ✅ Translate full summary to Hindi
            translated_text = translator.translate(full_summary, dest="hi").text

            # ✅ Generate Hindi Audio Summary using a POST request
            tts_response = requests.post("http://127.0.0.1:8000/generate_tts/", json={"text": translated_text})

            if tts_response.status_code == 200:
                audio_file = tts_response.json()["audio_file"]
                st.write("### 🔊 Listen to Summary in Hindi")
                st.audio(audio_file, format="audio/mp3")

            # ✅ Display Final Sentiment Analysis
            st.write("### 🔥 Final Sentiment Analysis")
            st.write(f"**{data['Final Sentiment Analysis']}**")

    else:
        st.error("❌ Failed to fetch news!")
