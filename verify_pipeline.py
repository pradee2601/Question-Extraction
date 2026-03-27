import os
import sys
from config import Config
from rag.embedder import Embedder
from rag.vector_store import VectorStore
# from rag.generator import Generator # Generator requires API key, tested implicitly via embeddings

def test_config():
    print("Testing Configuration...")
    if not Config.GOOGLE_API_KEY:
        print("❌ GOOGLE_API_KEY is missing! (Check .env)")
    else:
        print("✅ GOOGLE_API_KEY is present.")
        
    if not os.path.exists(Config.TESSERACT_CMD_PATH):
        print(f"❌ Tesseract not found at {Config.TESSERACT_CMD_PATH}")
    else:
        print(f"✅ Tesseract found at {Config.TESSERACT_CMD_PATH}")

def test_embedding():
    print("\nTesting Embedder...")
    try:
        if not Config.GOOGLE_API_KEY or Config.GOOGLE_API_KEY == "your_api_key_here":
            print("⚠️ Skipping Test: Valid API Key required.")
            return

        embedder = Embedder()
        emb = embedder.get_embedding("Test question")
        if emb and len(emb) == 768:
            print("✅ Embedding successful (dimension 768).")
        else:
            print(f"❌ Embedding failed or wrong dimension: {len(emb) if emb else 'None'}")
    except Exception as e:
        print(f"❌ Embedding error: {e}")

def test_vector_store():
    print("\nTesting Vector Store...")
    try:
        vs = VectorStore()
        # Mock data (dimension 768)
        emb = [0.1] * 768
        meta = {"id": "test", "text": "test"}
        vs.add_embeddings([emb], [meta])
        
        # Search
        res, dist = vs.search(emb)
        if len(res) > 0 and res[0]['id'] == 'test':
             print("✅ Vector Store add/search successful.")
        else:
             print("❌ Vector Store search failed.")
    except Exception as e:
        print(f"❌ Vector Store error: {e}")

if __name__ == "__main__":
    test_config()
    test_vector_store() # Can run without API key
    test_embedding()
