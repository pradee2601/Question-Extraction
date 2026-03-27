from rag.embedder import Embedder
from rag.vector_store import VectorStore
from utils.logger import setup_logger

logger = setup_logger(__name__)

class Retriever:
    def __init__(self):
        self.embedder = Embedder()
        self.vector_store = VectorStore()
        
        # Try to load existing index
        if not self.vector_store.load_index():
            logger.info("No existing index found. You need to ingest data first.")

    def retrieve(self, query_text, k=5, filters=None):
        # Generate embedding for query
        query_embedding = self.embedder.get_embedding(query_text)
        if not query_embedding:
            return []
            
        # Search vector store
        results, distances = self.vector_store.search(query_embedding, k)
        
        # Apply filters (Post-retrieval filtering)
        # Note: This is inefficient if k is small and filters are strict.
        # For better performance, we'd need a vector store with native filtering support (e.g. Chroma, Qdrant)
        # or separate indices for different categories.
        filtered_results = []
        for res in results:
            if filters:
                match = True
                for key, value in filters.items():
                    # Simple equality check for now
                    if key in res and str(res.get(key)).lower() != str(value).lower():
                        match = False
                        break
                if match:
                    filtered_results.append(res)
            else:
                filtered_results.append(res)
                
        return filtered_results
