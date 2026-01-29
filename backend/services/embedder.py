from sentence_transformers import SentenceTransformer
from typing import List, Union
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

class EmbeddingService:
    """Service for generating and comparing text embeddings"""
    
    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
        """Initialize the embedding model"""
        self.model = SentenceTransformer(model_name)
        
    def encode(self, texts: Union[str, List[str]]) -> np.ndarray:
        """
        Generate embeddings for text(s)
        
        Returns:
            numpy array of embeddings (2D: N x D)
        """
        return self.model.encode(texts, convert_to_numpy=True)
    
    def compute_similarity(self, text1: str, text2: str) -> float:
        """
        Compute cosine similarity between two texts
        """
        embeddings = self.encode([text1, text2])
        # embeddings is (2, D)
        similarity = cosine_similarity(embeddings[0:1], embeddings[1:2])[0][0]
        return float(similarity)
    
    def compute_similarity_batch(self, query: str, documents: List[str]) -> List[float]:
        """
        Compute similarity between a query and multiple documents
        """
        query_embedding = self.encode(query) # query_embedding is (D,) or (1, D)
        if query_embedding.ndim == 1:
            query_embedding = query_embedding.reshape(1, -1)
        elif query_embedding.ndim == 2 and query_embedding.shape[0] == 1:
            pass # already (1, D)
            
        doc_embeddings = self.encode(documents) # doc_embeddings is (N, D)
        
        similarities = cosine_similarity(query_embedding, doc_embeddings)[0]
        return similarities.tolist()
    
    def find_most_similar(self, query: str, documents: List[str]) -> tuple[int, float]:
        """
        Find the most similar document to a query
        
        Args:
            query: Query text
            documents: List of document texts
            
        Returns:
            Tuple of (index, similarity_score)
        """
        similarities = self.compute_similarity_batch(query, documents)
        max_idx = int(np.argmax(similarities))
        max_score = float(similarities[max_idx])
        return max_idx, max_score

# Global instance
_embedding_service = None

def get_embedding_service() -> EmbeddingService:
    """Get or create the global embedding service instance"""
    global _embedding_service
    if _embedding_service is None:
        _embedding_service = EmbeddingService()
    return _embedding_service
