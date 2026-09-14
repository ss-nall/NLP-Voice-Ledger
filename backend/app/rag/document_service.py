"""
Document Intelligence & RAG Retrieval Service.
Extracts context from unstructured business documents and answers questions
with grounded source citations.
"""

from typing import Dict, Any, List
from sqlalchemy.orm import Session
from backend.app.database.models import BusinessDocument
from backend.app.rag.vector_store import vector_store

class DocumentService:
    @staticmethod
    def sync_documents_from_db(db: Session):
        docs = db.query(BusinessDocument).all()
        doc_list = [
            {
                "id": d.id,
                "title": d.title,
                "doc_type": d.doc_type,
                "content": d.content
            }
            for d in docs
        ]
        vector_store.documents = []
        vector_store.add_documents(doc_list)

    @classmethod
    def query_documents(cls, db: Session, question: str) -> Dict[str, Any]:
        cls.sync_documents_from_db(db)
        search_results = vector_store.search(question, top_k=2)
        
        if not search_results:
            return {
                "question": question,
                "answer": "No matching business documents, invoices, or store policies found for this query.",
                "sources": []
            }
            
        top_match = search_results[0]["document"]
        content = top_match["content"]
        title = top_match["title"]
        
        # Format a clear, grounded contextual response
        answer = f"Based on '{title}':\n{content.strip()}"
        
        sources = [
            {
                "title": r["document"]["title"],
                "doc_type": r["document"]["doc_type"],
                "score": r["relevance_score"]
            }
            for r in search_results
        ]
        
        return {
            "question": question,
            "answer": answer,
            "sources": sources
        }

# Global singleton
document_service = DocumentService()
