import os
import sys
from config import Config
from rag.embedder import Embedder
from rag.vector_store import VectorStore
# from rag.generator import Generator # Generator requires API key, tested implicitly via embeddings

def test_config():
    print("Testing Configuration...")
    if not (Config.API_KEY or Config.GOOGLE_API_KEY):
        print("[ERROR] No Generation API Key found (API_KEY, API-Key, or GOOGLE_API_KEY)! (Check .env)")
    else:
        print("[OK] Generation API Key is present.")
        
    if not os.path.exists(Config.TESSERACT_CMD_PATH):
        print(f"[ERROR] Tesseract not found at {Config.TESSERACT_CMD_PATH}")
    else:
        print(f"[OK] Tesseract found at {Config.TESSERACT_CMD_PATH}")

def test_embedding():
    print("\nTesting Embedder...")
    try:
        if not Config.GOOGLE_API_KEY or Config.GOOGLE_API_KEY == "your_api_key_here":
            print("⚠️ Skipping Test: Valid API Key required.")
            return

        embedder = Embedder()
        emb = embedder.get_embedding("Test question")
        if emb and len(emb) == 768:
            print("[OK] Embedding successful (dimension 768).")
        else:
            print(f"[ERROR] Embedding failed or wrong dimension: {len(emb) if emb else 'None'}")
    except Exception as e:
        print(f"[ERROR] Embedding error: {e}")

def test_vector_store():
    print("\nTesting Vector Store...")
    try:
        vs = VectorStore()
        # Mock data (dimension 3072)
        emb = [0.1] * 3072
        meta = {"id": "test", "text": "test"}
        vs.add_embeddings([emb], [meta])
        
        # Search
        res, dist = vs.search(emb)
        if len(res) > 0 and res[0]['id'] == 'test':
             print("[OK] Vector Store add/search successful.")
        else:
             print("[ERROR] Vector Store search failed.")
    except Exception as e:
        print(f"[ERROR] Vector Store error: {e}")

def test_llm():
    print(f"\nTesting {Config.GENERATION_MODEL} API...")
    from utils.helpers import call_llm
    try:
        resp = call_llm("Say OK")
        if resp:
            print(f"[OK] LLM response: {resp.strip()}")
        else:
            print("[ERROR] LLM returned empty response.")
    except Exception as e:
        print(f"[ERROR] LLM error: {e}")

if __name__ == "__main__":
    test_config()
    test_vector_store() 
    test_llm()
    # test_embedding() # Requires Google API Key
