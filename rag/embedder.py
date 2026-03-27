import google.generativeai as genai
from config import Config
from utils.logger import setup_logger
import time

logger = setup_logger(__name__)

class Embedder:
    def __init__(self):
        if not Config.GOOGLE_API_KEY:
            logger.error("GOOGLE_API_KEY not found in environment variables.")
            raise ValueError("GOOGLE_API_KEY not found.")
            
        genai.configure(api_key=Config.GOOGLE_API_KEY)
        self.model = Config.EMBEDDING_MODEL

    def get_embedding(self, text, retries=5):
        """
        Get embedding for a single string with exponential backoff on quota limits.
        """
        try:
            if not text or len(text.strip()) == 0:
                return None
                
            for attempt in range(retries):
                try:
                    result = genai.embed_content(
                        model=self.model,
                        content=text,
                        task_type="retrieval_document"
                    )
                    return result['embedding']
                except Exception as e:
                    error_msg = str(e).lower()
                    if "429" in error_msg or "quota" in error_msg:
                        if attempt < retries - 1:
                            sleep_duration = 2 ** attempt + 3 # 4s, 5s, 7s, 11s...
                            logger.warning(f"Rate limited (429). Retrying in {sleep_duration}s... (Attempt {attempt+1}/{retries})")
                            time.sleep(sleep_duration)
                            continue
                    
                    logger.error(f"Embedding failed for text '{text[:30]}...': {e}")
                    return None
                    
        except Exception as e:
            logger.error(f"Unexpected error in embedding logic: {e}")
            return None
            
    def get_embeddings_batch(self, texts, batch_size=10):
        """
        Get embeddings for a list of texts.
        """
        embeddings = []
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i+batch_size]
            try:
                # Note: valid_models = ['models/embedding-001'] support batch embedding
                # but currently genai.embed_content is single or handled differently.
                # We will iterate for now to be safe with error handling.
                # If the API supports batch, we can optimize.
                
                for text in batch:
                    # Rate limiting sleep
                    time.sleep(0.2) 
                    emb = self.get_embedding(text)
                    if emb:
                        embeddings.append(emb)
                    else:
                        # Handle failed embedding (maybe placeholder or skip)
                        # For RAG, we might want to skip or retry
                        logger.warning(f"Skipping empty embedding for text: {text[:20]}...")
                        
            except Exception as e:
                logger.error(f"Batch embedding failed: {e}")
        
        return embeddings
