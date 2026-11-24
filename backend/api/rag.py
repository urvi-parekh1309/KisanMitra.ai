from fastapi import APIRouter, Query
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional
from services.rag_service import rag_service

router = APIRouter(prefix="/rag", tags=["RAG Knowledge Base"])


class RAGQueryRequest(BaseModel):
    query: str = Field(..., description="Query to search within the agricultural vector database")
    top_k: int = Field(default=4, description="Number of document chunks to retrieve")


@router.get("/status", response_model=Dict[str, Any])
def get_rag_status():
    """Returns the operational status, chunk count, and storage details of the RAG vector store."""
    return rag_service.get_status()


@router.post("/query", response_model=Dict[str, Any])
def query_rag_knowledge_base(request: RAGQueryRequest):
    """Direct semantic retrieval endpoint to inspect retrieved chunks, metadata, and relevance scores."""
    return rag_service.retrieve(query=request.query, top_k=request.top_k)


@router.post("/reindex", response_model=Dict[str, Any])
def reindex_documents():
    """Forces re-ingestion and vectorization of all agricultural documents in the knowledge base."""
    return rag_service.initialize(force_reindex=True)
