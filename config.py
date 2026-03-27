import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
    TESSERACT_CMD_PATH = os.getenv("TESSERACT_CMD_PATH", r"C:\Program Files\Tesseract-OCR\tesseract.exe")
    SERPER_API = os.getenv("SERPER_API", "")
    FIRECRAWL_API = os.getenv("FIRECRAWL_API", "")
    
    DATASET_NAME = "Reja1/jee-neet-benchmark"
    
    # Paths
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    DATA_DIR = os.path.join(BASE_DIR, "data")
    RAW_DATA_DIR = os.path.join(DATA_DIR, "raw")
    PROCESSED_DATA_DIR = os.path.join(DATA_DIR, "processed")
    FAISS_INDEX_PATH = os.path.join(BASE_DIR, "faiss_index.bin")
    
    # Models
    EMBEDDING_MODEL = "models/gemini-embedding-001"
    GENERATION_MODEL = "gemini-3.1-flash-lite-preview"
    
    # Logging
    LOG_FILE = os.path.join(BASE_DIR, "app.log")
