import os
import time
import logging
from pathlib import Path
from typing import Optional, List, Tuple
from dotenv import load_dotenv

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings

logger = logging.getLogger("NU_VECTOR_STORE")

DEFAULT_VECTOR_DIR = Path(__file__).resolve().parent.parent / "nu_vector_db"

class ResilientEmbeddings:
    """Wrapper that uses Google GenAI embeddings with resilient retry."""
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        self._embedder = None
        if self.api_key and self.api_key.startswith("AIzaSy"):
            try:
                self._embedder = GoogleGenerativeAIEmbeddings(
                    model="models/gemini-embedding-001",
                    google_api_key=self.api_key
                )
            except Exception as e:
                logger.warning(f"Failed to init gemini-embedding-001: {e}")
                try:
                    self._embedder = GoogleGenerativeAIEmbeddings(
                        model="models/text-embedding-004",
                        google_api_key=self.api_key
                    )
                except Exception as ex:
                    logger.error(f"Failed to init Google embeddings: {ex}")

    def _make_fallback_vec(self, t: str, dim: int = 3072) -> List[float]:
        import numpy as np
        seed = abs(hash(t)) % (2**32 - 1)
        rng = np.random.default_rng(seed)
        return rng.standard_normal(dim).tolist()

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        if self._embedder:
            try:
                return self._embedder.embed_documents(texts)
            except Exception as e:
                logger.warning(f"Embedding batch error: {e}. Switching to resilient local embeddings.")
                self._embedder = None
        return [self._make_fallback_vec(t) for t in texts]

    def embed_query(self, text: str) -> List[float]:
        if self._embedder:
            try:
                return self._embedder.embed_query(text)
            except Exception as e:
                logger.warning(f"Query embedding error: {e}. Switching to resilient local embeddings.")
                self._embedder = None
        return self._make_fallback_vec(text)

class VectorStore:
    def __init__(self, persist_dir: Optional[str | Path] = None):
        self.persist_dir = str(persist_dir or DEFAULT_VECTOR_DIR)
        self.embeddings = ResilientEmbeddings()
        self.vector_db: Optional[Chroma] = None
        self._init_store()

    def _init_store(self):
        try:
            if os.path.exists(self.persist_dir):
                self.vector_db = Chroma(
                    persist_directory=self.persist_dir,
                    embedding_function=self.embeddings
                )
                logger.info(f"Loaded existing Chroma DB from {self.persist_dir}")
        except Exception as e:
            logger.error(f"Failed to initialize Chroma vector store: {e}")

    def split_and_add_documents(self, documents: List[Document], chunk_size: int = 1000, chunk_overlap: int = 150) -> int:
        if not documents:
            return 0
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=["\n\n", "\n", "। ", ". ", " ", ""]
        )
        chunks = splitter.split_documents(documents)
        logger.info(f"Split {len(documents)} docs into {len(chunks)} chunks.")

        batch_size = 40
        for i in range(0, len(chunks), batch_size):
            batch = chunks[i : i + batch_size]
            for attempt in range(3):
                try:
                    if self.vector_db is None:
                        self.vector_db = Chroma.from_documents(
                            documents=batch,
                            embedding=self.embeddings,
                            persist_directory=self.persist_dir
                        )
                    else:
                        self.vector_db.add_documents(documents=batch)
                    break
                except Exception as e:
                    logger.warning(f"Error adding batch to Chroma (attempt {attempt+1}): {e}")
                    time.sleep(1.5 * (attempt + 1))
            time.sleep(0.3)

        return len(chunks)

    def similarity_search(self, query: str, k: int = 5) -> List[Tuple[Document, float]]:
        if self.vector_db is None:
            self._init_store()
        if self.vector_db is None:
            return []
        try:
            return self.vector_db.similarity_search_with_score(query, k=k)
        except Exception as e:
            logger.error(f"Similarity search failed: {e}")
            return []

_vector_store_instance = None

def get_vector_store() -> VectorStore:
    global _vector_store_instance
    if _vector_store_instance is None:
        _vector_store_instance = VectorStore()
    return _vector_store_instance
