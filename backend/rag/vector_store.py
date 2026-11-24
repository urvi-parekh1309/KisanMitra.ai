import json
import sqlite3
import numpy as np
from pathlib import Path
from typing import List, Dict, Any, Optional
from .text_splitter import Chunk

# Try ChromaDB
HAS_CHROMADB = False
try:
    import chromadb
    # Test if chromadb actually initializes without DLL load failure
    _test_client = chromadb.Client()
    HAS_CHROMADB = True
except Exception:
    HAS_CHROMADB = False


class SQLiteVectorStore:
    """
    Robust, pure-Python persistent vector store powered by standard library SQLite.
    Zero external C-extension/DLL dependencies — guaranteed to run seamlessly
    under any restricted sandbox or OS environment.
    """

    def __init__(self, db_path: Path, collection_name: str = "agritech_knowledge_base"):
        self.db_path = Path(db_path)
        self.collection_name = collection_name
        self.db_file = self.db_path / f"{collection_name}.db"
        self._init_db()

    def _get_connection(self):
        return sqlite3.connect(str(self.db_file))

    def _init_db(self):
        self.db_path.mkdir(parents=True, exist_ok=True)
        with self._get_connection() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS chunks (
                    id TEXT PRIMARY KEY,
                    content TEXT NOT NULL,
                    metadata TEXT NOT NULL,
                    embedding BLOB NOT NULL
                )
            """)
            conn.commit()

    def count(self) -> int:
        with self._get_connection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT COUNT(*) FROM chunks")
            return cur.fetchone()[0]

    def add_chunks(self, chunks: List[Chunk], embeddings: List[List[float]]) -> int:
        records = []
        for chunk, emb in zip(chunks, embeddings):
            emb_blob = np.array(emb, dtype=np.float32).tobytes()
            meta_json = json.dumps(chunk.metadata, ensure_ascii=False)
            records.append((chunk.chunk_id, chunk.content, meta_json, emb_blob))

        with self._get_connection() as conn:
            conn.executemany("""
                INSERT OR REPLACE INTO chunks (id, content, metadata, embedding)
                VALUES (?, ?, ?, ?)
            """, records)
            conn.commit()
        return len(records)

    def query(self, query_embedding: List[float], top_k: int = 4) -> List[Dict[str, Any]]:
        if not query_embedding or self.count() == 0:
            return []

        q_vec = np.array(query_embedding, dtype=np.float32)
        q_norm = np.linalg.norm(q_vec)
        if q_norm < 1e-6:
            return []
        q_vec = q_vec / q_norm

        with self._get_connection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT id, content, metadata, embedding FROM chunks")
            rows = cur.fetchall()

        scores = []
        for row_id, content, meta_json, emb_blob in rows:
            emb_vec = np.frombuffer(emb_blob, dtype=np.float32)
            emb_norm = np.linalg.norm(emb_vec)
            if emb_norm > 1e-6:
                cosine_sim = float(np.dot(q_vec, emb_vec) / emb_norm)
            else:
                cosine_sim = 0.0

            scores.append({
                "id": row_id,
                "content": content,
                "metadata": json.loads(meta_json),
                "distance": 1.0 - cosine_sim,
                "similarity": round(max(0.0, min(1.0, cosine_sim)), 4)
            })

        # Sort descending by similarity
        scores.sort(key=lambda x: x["similarity"], reverse=True)
        return scores[:top_k]

    def clear(self):
        with self._get_connection() as conn:
            conn.execute("DELETE FROM chunks")
            conn.commit()


class AgriculturalVectorStore:
    """
    Unified Vector Store interface.
    Prefers ChromaDB when native bindings are accessible;
    falls back cleanly to SQLiteVectorStore in restricted sandbox environments.
    """

    def __init__(self, persist_dir: Path, collection_name: str = "agritech_knowledge_base"):
        self.persist_dir = Path(persist_dir)
        self.persist_dir.mkdir(parents=True, exist_ok=True)
        self.collection_name = collection_name
        self.backend = None

        if HAS_CHROMADB:
            try:
                self.client = chromadb.PersistentClient(path=str(self.persist_dir))
                self.collection = self.client.get_or_create_collection(
                    name=self.collection_name,
                    metadata={"hnsw:space": "cosine"}
                )
                self.backend = "chromadb"
                print(f"[VectorStore] ChromaDB active at {self.persist_dir} ({self.collection.count()} chunks)")
            except Exception as e:
                print(f"[VectorStore] ChromaDB initialization failed: {e}. Falling back to SQLite.")

        if not self.backend:
            self.sqlite_store = SQLiteVectorStore(self.persist_dir, self.collection_name)
            self.backend = "sqlite"
            print(f"[VectorStore] SQLite Vector Store active at {self.persist_dir} ({self.sqlite_store.count()} chunks)")

    def count(self) -> int:
        if self.backend == "chromadb":
            return self.collection.count()
        return self.sqlite_store.count()

    def add_chunks(self, chunks: List[Chunk], embeddings: List[List[float]], batch_size: int = 50) -> int:
        if self.backend == "chromadb":
            total_added = 0
            for i in range(0, len(chunks), batch_size):
                chunk_batch = chunks[i:i + batch_size]
                emb_batch = embeddings[i:i + batch_size]

                ids = [c.chunk_id for c in chunk_batch]
                documents = [c.content for c in chunk_batch]
                metadatas = []
                for c in chunk_batch:
                    clean_meta = {}
                    for k, v in c.metadata.items():
                        clean_meta[k] = v if isinstance(v, (str, int, float, bool)) else str(v)
                    metadatas.append(clean_meta)

                self.collection.upsert(
                    ids=ids,
                    documents=documents,
                    metadatas=metadatas,
                    embeddings=emb_batch
                )
                total_added += len(chunk_batch)
            return total_added
        else:
            return self.sqlite_store.add_chunks(chunks, embeddings)

    def query(self, query_embedding: List[float], top_k: int = 4) -> List[Dict[str, Any]]:
        if self.backend == "chromadb":
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=min(top_k, self.collection.count()),
                include=["documents", "metadatas", "distances"]
            )
            formatted = []
            if results and "documents" in results and results["documents"]:
                docs = results["documents"][0]
                metas = results["metadatas"][0] if "metadatas" in results else [{}] * len(docs)
                dists = results["distances"][0] if "distances" in results else [0.0] * len(docs)
                ids = results["ids"][0] if "ids" in results else [""] * len(docs)

                for doc_id, doc_text, meta, dist in zip(ids, docs, metas, dists):
                    sim = max(0.0, min(1.0, 1.0 - dist))
                    formatted.append({
                        "id": doc_id,
                        "content": doc_text,
                        "metadata": meta,
                        "distance": float(dist),
                        "similarity": round(float(sim), 4)
                    })
            return formatted
        else:
            return self.sqlite_store.query(query_embedding, top_k=top_k)

    def clear(self):
        if self.backend == "chromadb":
            try:
                self.client.delete_collection(self.collection_name)
                self.collection = self.client.get_or_create_collection(
                    name=self.collection_name,
                    metadata={"hnsw:space": "cosine"}
                )
            except Exception as e:
                print(f"[VectorStore] ChromaDB clear error: {e}")
        else:
            self.sqlite_store.clear()
