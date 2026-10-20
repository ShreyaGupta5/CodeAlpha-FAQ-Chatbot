# 🤖 CodeAlpha Task 2: Chatbot for FAQs

An intelligent, NLP-driven Question Answering Chatbot built for **CodeAlpha Internship Task 2**. It analyzes incoming user queries using natural language preprocessing, tokenization, lemmatization, and TF-IDF Cosine Similarity to find and display the most relevant FAQ answers in real time.

---

## 📌 Project Objectives & Requirements

| Requirement | Implementation Status | Description |
| :--- | :---: | :--- |
| **Collect FAQs** | ✅ Complete | Curated dataset with 20 real-world customer service FAQs across 7 categories in both JSON and CSV formats. |
| **Preprocess Text** | ✅ Complete | Custom NLTK pipeline: lowercasing, punctuation stripping, tokenization, stopword removal, and WordNet lemmatization. |
| **Similarity Matching** | ✅ Complete | TF-IDF representation (unigrams + bigrams) with Scikit-Learn Cosine Similarity scoring. |
| **Chatbot Response** | ✅ Complete | Displays best answer with confidence metric, category tag, and related question suggestions. |
| **Chat UI (Optional)** | ✅ Complete | Glassmorphic Dark/Light Web Interface with voice read-aloud, quick prompt pills, and FAQ explorer drawer. |

---

## 🏗️ Architecture & NLP Pipeline

```
User Input Query
       │
       ▼
1. NLP Preprocessing (nlp_preprocessor.py)
   ├── Lowercase & Regex Noise Removal
   ├── NLTK Word Tokenization
   ├── Intelligent Stopwords Removal
   └── WordNet Lemmatizer (Noun & Verb forms)
       │
       ▼
2. Vectorization & Similarity Engine (faq_matcher.py)
   ├── TF-IDF Vector Space (N-gram range: 1 to 2)
   ├── Cosine Similarity Calculation
   └── Confidence Scoring & Top-K Ranking
       │
       ▼
3. Chatbot Controller (chatbot.py / app.py)
   ├── If Score >= Threshold (0.25): Display Exact Answer
   └── If Score < Threshold: Friendly Fallback & Topic Suggestions
       │
       ▼
4. Output Interfaces
   ├── Terminal CLI (Interactive Shell)
   └── Web Application (Flask + Glassmorphic UI)
```

---

## 📁 Project Directory Structure

```text
CodeAlpha_Task 2_Chatbot for FAQs/
│
├── faq_data.json          # Primary FAQ knowledge base (questions, answers, pattern variants)
├── faqs.csv               # CSV formatted FAQ catalog (easy to view in Excel / Google Sheets)
├── nlp_preprocessor.py    # NLTK text cleaner, tokenizer, stopword remover & lemmatizer
├── faq_matcher.py         # TF-IDF vectorizer and Cosine Similarity matcher
├── chatbot.py             # Chatbot controller class & interactive CLI application
├── app.py                 # Flask web server exposing REST API endpoints
├── test_chatbot.py        # Automated test suite (6 passing unit/integration tests)
│
├── templates/
│   └── index.html         # Modern HTML5 Chatbot interface
│
├── static/
│   ├── style.css          # Vanilla CSS design system (glassmorphism, dark/light mode)
│   └── script.js          # Dynamic frontend logic, fetch API, voice synthesis, FAQ drawer
│
├── requirements.txt       # Python dependencies
├── run.bat                # 1-click Windows launcher for Web App
├── run_cli.bat            # 1-click Windows launcher for CLI mode
└── README.md              # Project documentation
```

---

## 🚀 Quick Start Guide

### 1. Prerequisites
Ensure **Python 3.10+** is installed on your system.

### 2. Install Dependencies
Open your terminal inside this folder and run:
```bash
pip install -r requirements.txt
```

### 3. Run the Web Application
Double-click `run.bat` or run:
```bash
python app.py
```
Open your browser and navigate to:
👉 **`http://127.0.0.1:5000`**

### 4. Run the Terminal (CLI) Interface
Double-click `run_cli.bat` or run:
```bash
python chatbot.py
```
Type any question or use helper commands like `help`, `faqs`, `clear`, or `exit`.

### 5. Run the Automated Tests
Run the unit test suite to verify matching accuracy and NLP preprocessing:
```bash
python test_chatbot.py
```

---

## 💡 Key Features

- **High Precision Matching**: Utilizes TF-IDF with sublinear term frequency and bigrams to understand user phrasing.
- **Out-of-Domain Guard**: Gracefully detects when a query does not match the FAQ database and provides smart suggestions.
- **Glassmorphic UI**: Ultra-modern responsive interface with dark/light themes, glowing status indicators, and smooth animations.
- **Text-to-Speech Aloud**: Built-in audio playback using the browser's Web Speech API.
- **FAQ Explorer Drawer**: Searchable directory to browse and click any FAQ to ask it instantly.
- **One-Click Launchers**: `.bat` files for effortless execution on Windows.
