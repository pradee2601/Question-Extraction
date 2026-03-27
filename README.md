# JEE/NEET MCQ Generator with RAG

This application generates MCQs for JEE/NEET exams using RAG (Retrieval Augmented Generation) with Google Gemini and FAISS.

## Prerequisites

1.  **Python 3.10+**
2.  **Tesseract OCR**:
    - Download and install from [UB-Mannheim/tesseract](https://github.com/UB-Mannheim/tesseract/wiki).
    - Ensure installation path matches `.env` (Default: `C:\Program Files\Tesseract-OCR\tesseract.exe`).
3.  **Google Gemini API Key**:
    - Get a key from [Google AI Studio](https://makersuite.google.com/app/apikey).

## Setup

1.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

2.  **Configure Environment**:
    - Edit `.env` file.
    - Set `GOOGLE_API_KEY`.
    - Set `TESSERACT_CMD_PATH` if different.

3.  **Run the App**:
    ```bash
    streamlit run app.py
    ```

## Usage

1.  **Initialize Knowledge Base**:
    - Go to Sidebar > Toggle "Update Knowledge Base".
    - Click "Ingest Data". 
    - *Note: This loads the dataset from HuggingFace, runs OCR on images, and builds the vector index. It may take some time.*

2.  **Generate MCQs**:
    - Select Exam, Subject, Difficulty.
    - Click "Generate MCQs".
    - View generated questions, answers, and explanations.

## Project Structure

- `app.py`: Main Streamlit application.
- `rag/`: RAG pipeline components (OCR, Embedder, VectorStore, Generator).
- `data/`: Data storage (handled by HuggingFace cache mostly).
- `utils/`: Helper functions.
- `prompts/`: Prompt templates.
