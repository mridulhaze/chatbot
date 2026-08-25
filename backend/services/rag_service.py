import re
import logging
from typing import List, Optional, Dict, Any, Tuple
from langchain_core.documents import Document

from backend.core.config import settings
from db.sql_store import get_sql_store
from db.vector_store import get_vector_store

logger = logging.getLogger("NU_RAG_SERVICE")

class RAGService:
    def __init__(self):
        self.sql_store = get_sql_store()
        self.vector_store = get_vector_store()

    def search_notices(self, query: str, category: Optional[str] = None, limit: int = 5) -> List[Dict[str, Any]]:
        """Searches scraped official university notices and circulars."""
        try:
            return self.sql_store.get_recent_notices(limit=limit, category=category)
        except Exception as e:
            logger.error(f"Error searching notices: {e}")
            return []

    def search_official_knowledge(self, query: str, limit: int = 4) -> List[Tuple[Document, float]]:
        """Searches crawled official website pages, departments, and syllabi from vector store with fast fallback."""
        try:
            # Query vector database filtering out support cases
            raw_results = self.vector_store.similarity_search(query, k=limit * 2)
            filtered = []
            for doc, score in raw_results:
                meta = doc.metadata or {}
                if meta.get("type") != "solved_support_case":
                    filtered.append((doc, score))
                if len(filtered) >= limit:
                    break
            if filtered:
                return filtered
        except Exception as e:
            logger.warning(f"Vector search bypassed/fallback: {e}")

        # High-speed SQLite fallback if vector store is rate-limited or empty
        try:
            from backend.crawler.db import get_crawler_db
            conn = get_crawler_db()
            cursor = conn.cursor()
            words = [w for w in query.split() if len(w) > 2][:3]
            if words:
                clause = " OR ".join(["title LIKE ? OR content_text LIKE ?"] * len(words))
                params = []
                for w in words:
                    params.extend([f"%{w}%", f"%{w}%"])
                cursor.execute(f"SELECT title, url, section, content_text FROM pages WHERE {clause} ORDER BY id DESC LIMIT ?", (*params, limit))
                rows = cursor.fetchall()
                conn.close()
                results = []
                for r in rows:
                    doc = Document(
                        page_content=f"Title: {r['title']}\n\n{r['content_text'][:600]}",
                        metadata={"title": r["title"], "url": r["url"], "section": r["section"]}
                    )
                    results.append((doc, 0.85))
                return results
            conn.close()
        except Exception as e2:
            logger.error(f"Fallback SQLite search error: {e2}")

        return []

_rag_service_instance: Optional[RAGService] = None

def get_rag_service() -> RAGService:
    global _rag_service_instance
    if _rag_service_instance is None:
        _rag_service_instance = RAGService()
    return _rag_service_instance
