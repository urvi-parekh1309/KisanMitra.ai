import re
from typing import List, Dict, Any, Optional
from .embedding_service import MultilingualEmbeddingService
from .vector_store import AgriculturalVectorStore

# Multilingual agricultural domain lexicon for hybrid query expansion
# Maps common Marathi, Hindi, and Gujarati terms to standardized concepts
AGRI_MULTILINGUAL_EXPANSION = {
    "कापूस": "cotton",
    "कपास": "cotton",
    "કપાસ": "cotton",
    "बोंडअळी": "bollworm pectinophora gossypiella",
    "गुलाबी बोंडअळी": "pink bollworm rosetted flowers",
    "गुलाबी सुंडी": "pink bollworm rosetted flowers",
    "सोयाबीन": "soybean glycine max",
    "पिवळा मोझॅक": "yellow mosaic virus whitefly bemisia tabaci",
    "पीला मोजेक": "yellow mosaic virus whitefly bemisia tabaci",
    "पाने पिवळी": "yellow leaves chlorosis iron deficiency",
    "पीली पत्तियां": "yellow leaves chlorosis",
    "गहू": "wheat triticum",
    "गेहूं": "wheat triticum",
    "ઘઉં": "wheat",
    "तांबेरा": "wheat rust puccinia",
    "गेरुआ": "wheat rust puccinia",
    "मूंगफली": "groundnut peanut calcium gypsum",
    "भुईमूग": "groundnut peanut calcium gypsum",
    "मગફળી": "groundnut peanut calcium gypsum",
    "कांदा": "onion allium cepa",
    "प्याज": "onion allium cepa",
    "ડુંગળી": "onion allium cepa",
    "करपा": "purple blotch alternaria porri",
    "जांभळा करपा": "purple blotch alternaria porri",
    "पाऊस": "heavy rainfall waterlogging drainage",
    "बारिश": "heavy rainfall waterlogging drainage",
    "વરસાદ": "heavy rainfall waterlogging drainage",
    "पाणी साचणे": "waterlogging standing water drainage",
    "जलभराव": "waterlogging standing water drainage",
    "खत": "fertilizer NPK dosage",
    "खाद": "fertilizer NPK dosage",
    "पेरणी": "sowing planting time",
    "बुवाई": "sowing planting time",
    "વાવણી": "sowing planting time"
}


class AgriculturalRetriever:
    """
    High-level semantic retriever for farmer queries.
    Features:
    1. Multilingual agricultural query expansion (Marathi, Hindi, Gujarati, English).
    2. Dense semantic similarity search via ChromaDB / Vector Store.
    3. Calibrated relevance threshold filtering and citation assembly.
    """

    def __init__(
        self,
        vector_store: AgriculturalVectorStore,
        embedding_service: MultilingualEmbeddingService,
        top_k: int = 4,
        similarity_threshold: float = 0.08  # Calibrated for multilingual cosine space
    ):
        self.vector_store = vector_store
        self.embedding_service = embedding_service
        self.top_k = top_k
        self.similarity_threshold = similarity_threshold

    def expand_query(self, query: str) -> str:
        """Expands query with cross-lingual agricultural synonyms."""
        expanded = query
        for indic_term, english_synonyms in AGRI_MULTILINGUAL_EXPANSION.items():
            if indic_term in query:
                expanded += f" {english_synonyms}"
        return expanded.strip()

    def retrieve(self, query: str, top_k: Optional[int] = None) -> Dict[str, Any]:
        k = top_k or self.top_k
        query_cleaned = query.strip()
        if not query_cleaned or self.vector_store.count() == 0:
            return {
                "query": query,
                "chunks": [],
                "context_text": "",
                "sources": [],
                "has_context": False
            }

        # 1. Expand query with cross-lingual agronomic terms
        enriched_query = self.expand_query(query_cleaned)

        # 2. Generate embedding
        query_embedding = self.embedding_service.get_embedding(enriched_query)
        if not query_embedding:
            return {
                "query": query,
                "chunks": [],
                "context_text": "",
                "sources": [],
                "has_context": False
            }

        # 3. Retrieve top-k nearest neighbors from Vector Store
        raw_results = self.vector_store.query(query_embedding, top_k=k)

        # 4. Filter by relevance threshold
        filtered_chunks = []
        for r in raw_results:
            if r["similarity"] >= self.similarity_threshold:
                filtered_chunks.append(r)

        # Negative test / out-of-domain guard:
        # If the top score is below the minimum threshold, reject it as irrelevant
        if not filtered_chunks:
            return {
                "query": query,
                "chunks": [],
                "context_text": "",
                "sources": [],
                "has_context": False
            }

        # 5. Assemble formatted context for prompt and citations for UI
        context_blocks = []
        sources = []
        seen_sources = set()

        for idx, item in enumerate(filtered_chunks, start=1):
            meta = item.get("metadata", {})
            source_file = meta.get("source", "Agricultural Advisory Document")
            page = meta.get("page", 1)
            content = item.get("content", "").strip()
            score = item.get("similarity", 0.0)

            context_blocks.append(
                f"[Document {idx} | Source: {source_file} (Page {page})]\n{content}"
            )

            source_key = f"{source_file}_p{page}"
            if source_key not in seen_sources:
                seen_sources.add(source_key)
                sources.append({
                    "id": idx,
                    "document": source_file,
                    "page": page,
                    "relevance_score": score,
                    "snippet": content[:180] + ("..." if len(content) > 180 else "")
                })

        assembled_context = "\n\n---\n\n".join(context_blocks)

        return {
            "query": query,
            "chunks": filtered_chunks,
            "context_text": assembled_context,
            "sources": sources,
            "has_context": True
        }
