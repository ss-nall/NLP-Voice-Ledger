"""
Hybrid Vector & Keyword Document Store for RAG.
Stores and searches unstructured business documents (Credit policies, Invoices, Agreements).
"""

import math
import re
from typing import Dict, Any, List, Tuple
from rank_bm25 import BM25Okapi

class SimpleVectorStore:
    def __init__(self):
        self.documents: List[Dict[str, Any]] = []
        self.bm25: BM25Okapi = None
        self.corpus_tokens: List[List[str]] = []
        
    def add_documents(self, docs: List[Dict[str, Any]]):
        self.documents.extend(docs)
        self._rebuild_index()
        
    def _tokenize(self, text: str) -> List[str]:
        return re.findall(r'\w+', text.lower())
        
    def _rebuild_index(self):
        if not self.documents:
            self.bm25 = None
            self.corpus_tokens = []
            return
            
        self.corpus_tokens = [self._tokenize(d["content"] + " " + d.get("title", "")) for d in self.documents]
        self.bm25 = BM25Okapi(self.corpus_tokens)
        
    def search(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        if not self.bm25 or not self.documents:
            return []
            
        q_tokens = self._tokenize(query)
        if not q_tokens:
            return []
            
        scores = self.bm25.get_scores(q_tokens)
        scored_docs = list(zip(self.documents, scores))
        scored_docs = sorted(scored_docs, key=lambda x: x[1], reverse=True)
        
        results = []
        for doc, score in scored_docs[:top_k]:
            if score > 0.05:
                results.append({
                    "document": doc,
                    "relevance_score": round(float(score), 3)
                })
        return results

# Global singleton
vector_store = SimpleVectorStore()
