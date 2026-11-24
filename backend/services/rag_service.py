from pathlib import Path
from typing import Dict, Any, Optional

from config import settings, DOCUMENTS_DIR, VECTOR_STORE_DIR
from rag.document_loader import AgriculturalDocumentLoader
from rag.text_splitter import AgriculturalTextSplitter
from rag.embedding_service import MultilingualEmbeddingService
from rag.vector_store import AgriculturalVectorStore
from rag.retriever import AgriculturalRetriever


class RAGService:
    """
    Central RAG orchestrator service.
    Connects Document Loader, Text Splitter, Multilingual Embedder,
    ChromaDB Vector Store, and Retriever.
    """

    def __init__(self):
        self.loader = AgriculturalDocumentLoader(documents_dir=DOCUMENTS_DIR)
        self.splitter = AgriculturalTextSplitter(
            chunk_size=settings.CHUNK_SIZE,
            chunk_overlap=settings.CHUNK_OVERLAP
        )
        self.embedder = MultilingualEmbeddingService(
            api_key=settings.GEMINI_API_KEY,
            model_name=settings.GEMINI_EMBEDDING_MODEL
        )
        self.vector_store = AgriculturalVectorStore(
            persist_dir=VECTOR_STORE_DIR,
            collection_name=settings.CHROMA_COLLECTION_NAME
        )
        self.retriever = AgriculturalRetriever(
            vector_store=self.vector_store,
            embedding_service=self.embedder,
            top_k=settings.TOP_K_RETRIEVAL,
            similarity_threshold=settings.SIMILARITY_THRESHOLD
        )
        self._is_initialized = False

    def initialize(self, force_reindex: bool = False) -> Dict[str, Any]:
        """
        Initializes the knowledge base.
        If the vector store is empty or force_reindex is True, ingests all documents.
        """
        current_count = self.vector_store.count()
        if current_count == 0 or force_reindex:
            print("[RAGService] Vector store empty or reindex requested. Ingesting documents...")
            stats = self.ingest_all_documents()
            self._is_initialized = True
            return stats

        print(f"[RAGService] Vector store already indexed with {current_count} chunks.")
        self._is_initialized = True
        return {
            "status": "ready",
            "existing_chunks": current_count,
            "reindexed": False
        }

    def ingest_all_documents(self) -> Dict[str, Any]:
        """Loads all documents from documents directory, chunks them, and stores in ChromaDB."""
        # 1. Load documents
        raw_docs = self.loader.load_all(DOCUMENTS_DIR)
        if not raw_docs:
            print(f"[RAGService] No documents found in {DOCUMENTS_DIR}")
            return {
                "status": "warning",
                "message": "No documents found to ingest",
                "documents_loaded": 0,
                "chunks_indexed": self.vector_store.count()
            }

        # 2. Split into chunks
        chunks = self.splitter.split_documents(raw_docs)
        if not chunks:
            return {
                "status": "warning",
                "message": "No chunks generated from documents",
                "documents_loaded": len(raw_docs),
                "chunks_indexed": 0
            }

        # 3. Compute embeddings
        texts = [c.content for c in chunks]
        print(f"[RAGService] Generating embeddings for {len(texts)} chunks...")
        embeddings = self.embedder.get_embeddings(texts)

        # 4. Upsert into ChromaDB
        added_count = self.vector_store.add_chunks(chunks, embeddings)

        return {
            "status": "success",
            "documents_loaded": len(raw_docs),
            "chunks_generated": len(chunks),
            "chunks_indexed": added_count,
            "total_chunks_in_db": self.vector_store.count()
        }

    def retrieve(self, query: str, top_k: Optional[int] = None) -> Dict[str, Any]:
        """Retrieves relevant chunks and context for a farmer's query."""
        return self.retriever.retrieve(query, top_k=top_k)

    def get_status(self) -> Dict[str, Any]:
        """Returns the operational status of the RAG pipeline."""
        return {
            "total_chunks": self.vector_store.count(),
            "collection_name": self.vector_store.collection_name,
            "persist_dir": str(self.vector_store.persist_dir),
            "embedding_mode": "Gemini API" if self.embedder.use_gemini else "Local Multilingual",
            "is_ready": self.vector_store.count() > 0
        }


# Global singleton instance
rag_service = RAGService()
