from typing import List, Dict, Any
from langchain_text_splitters import RecursiveCharacterTextSplitter
from .document_loader import Document


class Chunk:
    """Represents an atomic text chunk ready for vectorization and indexing."""
    def __init__(self, chunk_id: str, content: str, metadata: Dict[str, Any]):
        self.chunk_id = chunk_id
        self.content = content
        self.metadata = metadata

    def __repr__(self):
        return f"<Chunk id='{self.chunk_id}' len={len(self.content)} page={self.metadata.get('page')}>"


class AgriculturalTextSplitter:
    """
    Splits agricultural documents into semantically coherent chunks.
    Respects Devanagari sentence boundaries (danda '।') as well as standard punctuation.
    """

    def __init__(self, chunk_size: int = 600, chunk_overlap: int = 80):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

        # Separators prioritize natural paragraph breaks, Indic sentence terminators, and standard periods
        indic_separators = [
            "\n\n",
            "\n",
            "। ",   # Devanagari full stop (Purna Viram)
            ". ",
            "? ",
            "! ",
            " ",
            ""
        ]

        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            separators=indic_separators,
            length_function=len
        )

    def split_documents(self, documents: List[Document]) -> List[Chunk]:
        """Splits a list of Document objects into indexed Chunk objects."""
        chunks: List[Chunk] = []

        for doc in documents:
            raw_text = doc.content
            split_texts = self.splitter.split_text(raw_text)

            for idx, text in enumerate(split_texts):
                clean_text = text.strip()
                if len(clean_text) < 25:  # Skip tiny fragments
                    continue

                source_name = doc.metadata.get("source", "unknown")
                page_num = doc.metadata.get("page", 1)
                chunk_id = f"{source_name}_p{page_num}_c{idx}"

                chunk_meta = dict(doc.metadata)
                chunk_meta.update({
                    "chunk_id": chunk_id,
                    "chunk_index": idx,
                    "char_count": len(clean_text)
                })

                chunks.append(Chunk(
                    chunk_id=chunk_id,
                    content=clean_text,
                    metadata=chunk_meta
                ))

        print(f"[TextSplitter] Split {len(documents)} document pages into {len(chunks)} chunks.")
        return chunks
