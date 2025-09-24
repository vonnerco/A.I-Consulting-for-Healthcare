from sentence_transformers import SentenceTransformer
import chromadb

class VectorSearch:
    def __init__(self):
        self.embedder = SentenceTransformer('all-MiniLM-L6-v2')
        self.client = chromadb.Client()
        self.collection = self.client.get_collection("documents")
    
    def search(self, query: str, n_results: int = 5):
        query_embedding = self.embedder.encode([query])
        
        results = self.collection.query(
            query_embeddings=query_embedding.tolist(),
            n_results=n_results
        )
        
        return results
