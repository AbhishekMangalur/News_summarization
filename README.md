# Project documentation
# News Summarization and Text-to-Speech (TTS) Application

## 📌 Project Overview
This project is a **web-based application** that extracts key details from multiple news articles related to a given company, performs **sentiment analysis**, conducts a **comparative analysis**, and generates a **Hindi Text-to-Speech (TTS)** output.

The tool allows users to input a company name and receive a **structured sentiment report along with an audio summary**.

## 🚀 Features
- **News Extraction:** Fetches at least 10 unique news articles related to the given company.
- **Sentiment Analysis:** Analyzes each article as **Positive, Negative, or Neutral**.
- **Comparative Analysis:** Highlights sentiment variations across multiple articles.
- **Text-to-Speech (TTS) in Hindi:** Converts the news summary into **Hindi speech**.
- **User Interface (UI):** Simple and interactive UI using **Streamlit**.
- **API-Based Communication:** The frontend communicates with the backend via **FastAPI APIs**.
- **Deployment:** Deployed on **Hugging Face Spaces**.

---

## 📂 Project Structure
```
news_summarization/
│── app.py                 # Streamlit frontend
│── api.py                 # FastAPI backend
│── utils.py               # Helper functions (scraping, sentiment analysis, TTS)
│── requirements.txt       # Dependencies
│── README.md              # Project documentation
│── data/                  # Folder to store temporary audio files
│── templates/             # (Optional) For additional UI customization
│── static/                # (Optional) CSS, JS files
```

---

## 🛠️ Installation & Setup
### 1️⃣ Clone the Repository
```bash
git clone https://github.com/yourusername/news-summarization-tts.git
cd news-summarization-tts
```

### 2️⃣ Install Dependencies
```bash
pip install -r requirements.txt
```

### 3️⃣ Start the Backend (FastAPI)
```bash
uvicorn api:app --reload
```
✅ The API will run on **http://127.0.0.1:8000**.

### 4️⃣ Start the Frontend (Streamlit)
```bash
streamlit run app.py
```
✅ The UI will open in your browser.

---

## 📡 API Documentation
Once the backend is running, visit:
```
http://127.0.0.1:8000/docs
```
This page will show all available APIs.

### **1️⃣ Fetch News API**
- **Endpoint:** `/fetch_news/`
- **Method:** `GET`
- **Example Request:**
  ```bash
  curl "http://127.0.0.1:8000/fetch_news/?company=Tesla"
  ```
- **Example Response:**
  ```json
  {
    "company": "Tesla",
    "articles": [
      { "title": "Tesla’s stock surges", "summary": "Tesla saw record growth...", "sentiment": "Positive" },
      { "title": "Tesla faces legal issues", "summary": "Regulators raised concerns...", "sentiment": "Negative" }
    ]
  }
  ```

### **2️⃣ Generate Hindi TTS API**
- **Endpoint:** `/generate_tts/`
- **Method:** `GET`
- **Example Request:**
  ```bash
  curl "http://127.0.0.1:8000/generate_tts/?text=टेस्ला बहुत तेजी से बढ़ रहा है"
  ```
- **Example Response:**
  ```json
  { "audio_file": "data/output.mp3" }
  ```

---

## 🚀 Deployment
### 1️⃣ Deploy on Hugging Face Spaces
1. Create a **new Space** on [Hugging Face Spaces](https://huggingface.co/spaces).
2. Choose **Streamlit** as the framework.
3. Upload all project files.
4. Add a `requirements.txt` file with dependencies.
5. Deploy and get a public URL.

---

## 📜 License
This project is open-source and available under the **MIT License**.

---

## 🤝 Contributing
Feel free to **fork** the repository and submit **pull requests**. Let's improve this together! 🚀

---

## 📞 Contact
For questions or issues, contact:
📧 Email: `abhimangalur1@gmail.com`
📌 GitHub: [yourusername](https://github.com/yourusername)

