# AI Plagiarism Detection System

## Live Demo
Try out the deployed application here:

🚀 **Streamlit App** → (Add your Streamlit URL here once deployed)

## Overview
AI Plagiarism Detection is a Python-based application that analyzes input text and detects potential plagiarism by comparing it with content available on the web.

The system works by preprocessing text, splitting it into sentences, searching for similar content online, and calculating similarity scores to identify plagiarized portions.

This project focuses on building a simple, modular, and explainable plagiarism detection pipeline without training custom machine learning models, making it beginner-friendly and easy to extend.

## Features
- Paste and analyze text for plagiarism
- Sentence-level plagiarism detection
- Multi-source web searching (Wikipedia, DuckDuckGo, Google Custom Search)
- Real-time internet plagiarism detection
- Similarity score calculation for each sentence
- Internal duplicate detection
- Identifies best matching source URLs
- Adjustable similarity threshold
- Gemini AI integration for paraphrase detection
- Plagiarism submission guidance (0-15% excellent → 60%+ critical)
- Detailed statistical reports
- Modular AI pipeline design
- Simple and interactive Streamlit UI

## Tech Stack
- Python
- Streamlit
- sentence-transformers
- sklearn
- requests

## Project Structure

```text
AI_PLAGIARISM_DETECTION/
│
├── app.py                   # Streamlit application entry point
├── requirements.txt         # Project dependencies
├── README.md                # Project documentation
├──gitignore.txt
│             
├── ai_engine/
│   ├── text_processing.py     # Text cleaning and sentence splitting
│   ├── gemini_integration.py  # Integration of geminit api for plagiarism check
│   ├── web_search.py          # Web search logic for plagiarism detection
│   ├── similarity.py          # Text similarity computation
│   └── scoring.py             # Overall plagiarism scoring logic
│
└── screenshots/ # Application screenshots
    ├── home.png
    ├── upload.png
    └── result.png
```

## Screenshots

### Application Interface
![Application Interface](<screenshots/Screenshot 2025-12-28 231742.png>)

### Text Input
![Text Input](<screenshots/Screenshot 2025-12-28 231803.png>)

### Plagiarism % Output
![Plagiarism Output](<screenshots/Screenshot 2025-12-28 231834.png>)


## How It Works
1. The user pastes text into the Streamlit interface.
2. The text is cleaned and preprocessed.
3. The content is split into individual sentences.
4. Each sentence is searched across multiple web sources (Wikipedia, DuckDuckGo, and optionally Google).
5. Similarity scores are calculated between the input sentence and fetched snippets using sentence transformers.
6. Internal duplicates within the text are also detected.
7. The highest similarity score and corresponding source URL are identified for each sentence.
8. Results are analyzed with Gemini AI for paraphrase detection and plagiarism risk assessment.
9. A plagiarism report with statistical summary and submission guidance is generated.

## Installation & Setup
1. Open your IDE (VS Code is recommended).
2. Clone or download the project files to your local system.
3. Create a virtual environment to avoid dependency conflicts:
   ```bash
   python -m venv venv
   venv\Scripts\activate
4. Install the required dependencies:
    pip install -r requirements.txt
5. **(Optional) Configure Google Custom Search for enhanced web detection:**
   - Get a Google Custom Search API key from: https://developers.google.com/custom-search/v1/overview
   - Create a Custom Search Engine at: https://programmablesearchengine.google.com/
   - Set environment variables:
     ```bash
     # Windows (PowerShell)
     $env:GOOGLE_API_KEY="your_api_key_here"
     $env:GOOGLE_CX="your_cx_here"
     
     # Windows (CMD)
     set GOOGLE_API_KEY=your_api_key_here
     set GOOGLE_CX=your_cx_here
     
     # Linux/Mac
     export GOOGLE_API_KEY="your_api_key_here"
     export GOOGLE_CX="your_cx_here"
     ```
   - Without these keys, the app will still work using Wikipedia and DuckDuckGo search
6. Run the application:
    streamlit run app.py

## Usage
This application can be used to check whether a given text contains plagiarized content.
Users simply paste text into the interface and click Check Plagiarism.
The system analyzes each sentence, compares it with online sources, and displays similarity scores along with potential source URLs.
This makes it useful for students, educators, content creators, and researchers.

## Future Improvements
Percentage-based plagiarism summary
Highlight plagiarized sentences in the UI
Support for document uploads (PDF / DOCX)
Cached web search results for faster performance
Advanced semantic similarity using transformer models
Exportable plagiarism reports (PDF)

## Learning Outcomes
Through this project, I gained hands-on experience in building an end-to-end AI-powered text analysis system.
I learned how to preprocess text, integrate web search, compute similarity scores, and design a modular Python pipeline.This project strengthened my understanding of NLP workflows, Streamlit-based UI development, and real-world AI application design.