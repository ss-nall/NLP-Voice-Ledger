from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional, List
from pydantic import BaseModel
from backend.app.database.session import get_db
from backend.app.database.models import BusinessDocument
from backend.app.rag.document_service import document_service

router = APIRouter(prefix="/documents", tags=["Documents & RAG"])

class DocumentCreate(BaseModel):
    title: str
    doc_type: str = "INVOICE"
    content: str

class RAGQueryRequest(BaseModel):
    question: str

@router.get("/")
def list_documents(db: Session = Depends(get_db)):
    docs = db.query(BusinessDocument).order_by(BusinessDocument.created_at.desc()).all()
    return [
        {
            "id": d.id,
            "title": d.title,
            "doc_type": d.doc_type,
            "content": d.content,
            "created_at": d.created_at.isoformat()
        }
        for d in docs
    ]

@router.post("/")
def create_document(payload: DocumentCreate, db: Session = Depends(get_db)):
    doc = BusinessDocument(
        title=payload.title,
        doc_type=payload.doc_type,
        content=payload.content
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)
    document_service.sync_documents_from_db(db)
    return {"success": True, "id": doc.id, "title": doc.title}

@router.post("/rag-query")
def query_documents_rag(payload: RAGQueryRequest, db: Session = Depends(get_db)):
    if not payload.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty")
    return document_service.query_documents(db, payload.question)
