import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from backend.rag.document_loader import DocumentLoader

class PolicyVectorStore:
    """
    Vector search index for institutional policy documents using TF-IDF 
    and cosine similarity for robust, zero-latency retrieval.
    """
    def __init__(self, loader=None):
        self.loader = loader or DocumentLoader()
        self.vectorizer = TfidfVectorizer(ngram_range=(1, 2), stop_words="english")
        self.chunks = []
        self.tfidf_matrix = None
        self.is_indexed = False
        self.build_index()

    def build_index(self):
        self.chunks = self.loader.load_documents()
        if not self.chunks:
            return
        
        corpus = [f"{c['doc_title']} {c['section']} {c['content']}" for c in self.chunks]
        self.tfidf_matrix = self.vectorizer.fit_transform(corpus)
        self.is_indexed = True

    def search(self, query: str, top_k: int = 3) -> list:
        if not self.is_indexed or not self.chunks:
            self.build_index()
            if not self.is_indexed:
                return []

        query_vec = self.vectorizer.transform([query])
        similarities = cosine_similarity(query_vec, self.tfidf_matrix)[0]

        top_indices = np.argsort(similarities)[::-1][:top_k]
        results = []
        for idx in top_indices:
            score = float(similarities[idx])
            chunk = self.chunks[idx].copy()
            chunk["similarity_score"] = round(score, 4)
            results.append(chunk)
        return results
