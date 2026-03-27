import faiss
import numpy as np
import pickle
import os
from config import Config
from utils.logger import setup_logger

logger = setup_logger(__name__)

class VectorStore:
    def __init__(self, dimension=3072): # Gemini embedding-001 is 3072
        self.dimension = dimension
        self.index = faiss.IndexFlatL2(self.dimension)
        self.metadata = [] # To store question ID etc matching the index
        
    def add_embeddings(self, embeddings, metadatas):
        if len(embeddings) == 0:
            return
            
        embeddings_np = np.array(embeddings).astype('float32')
        if embeddings_np.shape[1] != self.dimension:
             logger.error(f"Dimension mismatch: Expected {self.dimension}, got {embeddings_np.shape[1]}")
             return

        self.index.add(embeddings_np)
        self.metadata.extend(metadatas)
        logger.info(f"Added {len(embeddings)} embeddings to store. Total: {self.index.ntotal}")
        
    def search(self, query_embedding, k=5):
        if len(query_embedding) == 0 or self.index.ntotal == 0:
            return [], []
            
        query_np = np.array([query_embedding]).astype('float32')
        distances, indices = self.index.search(query_np, k)
        
        results = []
        res_distances = []
        for i, idx in enumerate(indices[0]):
            if idx != -1 and idx < len(self.metadata):
                results.append(self.metadata[idx])
                res_distances.append(distances[0][i])
                
        return results, res_distances
        
    def save_index(self):
        try:
            faiss.write_index(self.index, Config.FAISS_INDEX_PATH)
            with open(Config.FAISS_INDEX_PATH + ".meta", "wb") as f:
                pickle.dump(self.metadata, f)
            logger.info("Index saved successfully.")
        except Exception as e:
            logger.error(f"Failed to save index: {e}")
            
    def load_index(self):
        try:
            if os.path.exists(Config.FAISS_INDEX_PATH) and os.path.exists(Config.FAISS_INDEX_PATH + ".meta"):
                self.index = faiss.read_index(Config.FAISS_INDEX_PATH)
                with open(Config.FAISS_INDEX_PATH + ".meta", "rb") as f:
                    self.metadata = pickle.load(f)
                logger.info(f"Index loaded successfully. Total vectors: {self.index.ntotal}")
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to load index: {e}")
            return False
