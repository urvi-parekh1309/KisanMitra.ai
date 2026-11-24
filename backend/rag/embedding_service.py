import hashlib
import math
import re
from typing import List, Optional
import numpy as np

try:
    from google import genai
    from google.genai import types
    HAS_NEW_GENAI = True
except Exception:
    HAS_NEW_GENAI = False

try:
    import google.generativeai as legacy_genai
    HAS_LEGACY_GENAI = True
except Exception:
    HAS_LEGACY_GENAI = False


class MultilingualEmbeddingService:
    """
    Multilingual Embedding Service supporting:
    1. Google Gemini text-embedding-004 (768-dim dense semantic embeddings)
    2. High-performance offline multilingual subword n-gram embedding fallback (384-dim)
       ensuring the system is always testable and operational offline.
    """

    def __init__(self, api_key: Optional[str] = None, model_name: str = "text-embedding-004"):
        self.api_key = api_key or ""
        self.model_name = model_name
        self.use_gemini = bool(self.api_key and self.api_key != "your_gemini_api_key_here")

        if self.use_gemini:
            if HAS_NEW_GENAI:
                try:
                    self.client = genai.Client(api_key=self.api_key)
                except Exception as e:
                    print(f"[EmbeddingService] Warning: Could not initialize modern genai Client: {e}")
                    self.client = None
            elif HAS_LEGACY_GENAI:
                try:
                    legacy_genai.configure(api_key=self.api_key)
                except Exception as e:
                    print(f"[EmbeddingService] Warning: Could not configure legacy genai: {e}")

    def _gemini_embed(self, texts: List[str]) -> Optional[List[List[float]]]:
        """Generates embeddings using Google Gemini API."""
        try:
            if HAS_NEW_GENAI and getattr(self, "client", None):
                response = self.client.models.embed_content(
                    model=self.model_name,
                    contents=texts
                )
                embeddings = [e.values for e in response.embeddings]
                return embeddings
            elif HAS_LEGACY_GENAI:
                result = legacy_genai.embed_content(
                    model=f"models/{self.model_name}",
                    content=texts,
                    task_type="retrieval_document"
                )
                if "embedding" in result:
                    emb = result["embedding"]
                    if emb and isinstance(emb[0], list):
                        return emb
                    return [emb]
        except Exception as e:
            print(f"[EmbeddingService] Gemini API embedding error: {e}. Falling back to offline multilingual embeddings.")
        return None

    @staticmethod
    def _offline_multilingual_embed(text: str, dim: int = 384) -> List[float]:
        """
        Deterministic, multilingual subword character n-gram hashing vectorizer.
        Generates dense, L2-normalized embeddings that capture morphological similarities
        across Marathi, Hindi, Gujarati, and English word stems.
        """
        vec = np.zeros(dim, dtype=np.float32)
        if not text:
            return vec.tolist()

        # Clean text and extract word tokens + character 3-grams/4-grams
        cleaned = text.lower().strip()
        words = re.findall(r"[\w\u0900-\u097F\u0A80-\u0AFF]+", cleaned)

        # 1. Word-level hashing
        for word in words:
            h = int(hashlib.md5(word.encode("utf-8")).hexdigest(), 16)
            idx = h % dim
            sign = 1.0 if (h // dim) % 2 == 0 else -1.0
            vec[idx] += sign * (1.0 + math.log(1.0 + len(word)))

            # 2. Subword 3-grams (critical for Indic agglutinative suffixes)
            if len(word) >= 3:
                for i in range(len(word) - 2):
                    ngram = word[i:i+3]
                    nh = int(hashlib.sha256(ngram.encode("utf-8")).hexdigest(), 16)
                    nidx = nh % dim
                    nsign = 1.0 if (nh // dim) % 2 == 0 else -1.0
                    vec[nidx] += 0.5 * nsign

        # L2-normalization for cosine distance
        norm = np.linalg.norm(vec)
        if norm > 1e-6:
            vec = vec / norm
        return vec.tolist()

    def get_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generates embeddings for a batch of text strings."""
        if not texts:
            return []

        if self.use_gemini:
            # Try Gemini API in batches of 16
            gemini_vectors: List[List[float]] = []
            batch_size = 16
            success = True

            for i in range(0, len(texts), batch_size):
                batch = texts[i:i + batch_size]
                batch_embeds = self._gemini_embed(batch)
                if batch_embeds and len(batch_embeds) == len(batch):
                    gemini_vectors.extend(batch_embeds)
                else:
                    success = False
                    break

            if success and len(gemini_vectors) == len(texts):
                return gemini_vectors

        # Fallback to local multilingual vectorizer
        return [self._offline_multilingual_embed(t) for t in texts]

    def get_embedding(self, text: str) -> List[float]:
        """Generates embedding for a single query or text."""
        res = self.get_embeddings([text])
        return res[0] if res else []
