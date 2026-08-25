import logging
from typing import Dict, Any, List, Optional

from backend.services.rag_service import get_rag_service
from db.sql_store import get_sql_store
from backend.crawler.db import get_db_connection

logger = logging.getLogger("NU_KNOWLEDGE_MCP_SERVER")

class KnowledgeMCPServer:
    """
    Official MCP Server for National University Knowledge Base & Verified Academic Pages.
    """
    def __init__(self):
        self.rag = get_rag_service()
        self.sql_store = get_sql_store()

    def search_nu_knowledge(self, query: str, section: Optional[str] = None, limit: int = 4) -> Dict[str, Any]:
        """
        MCP Tool: search_nu_knowledge
        Searches verified official university website pages, circulars, and departmental content.
        """
        try:
            results = self.rag.search_official_knowledge(query, limit=limit)
            data = [
                {
                    "content": doc.page_content,
                    "metadata": doc.metadata,
                    "score": float(score)
                }
                for doc, score in results
            ]
            return {"success": True, "data": data, "error": None}
        except Exception as e:
            logger.error(f"MCP search_nu_knowledge error: {e}", exc_info=True)
            return {"success": False, "data": None, "error": {"code": "KNOWLEDGE_SEARCH_FAILED", "message": str(e)}}

    def search_notices(self, query: str, category: Optional[str] = None, limit: int = 5) -> Dict[str, Any]:
        """
        MCP Tool: search_notices
        Searches recent official notices and circulars.
        """
        try:
            notices = self.rag.search_notices(query, category=category, limit=limit)
            return {"success": True, "data": notices, "error": None}
        except Exception as e:
            logger.error(f"MCP search_notices error: {e}", exc_info=True)
            return {"success": False, "data": None, "error": {"code": "NOTICE_SEARCH_FAILED", "message": str(e)}}

    # Backward compatibility alias
    search_notice = search_notices

    def search_exam_information(self, query: str, limit: int = 5) -> Dict[str, Any]:
        """
        MCP Tool: search_exam_information
        Retrieves examination routines, center lists, and circulars.
        """
        try:
            notices = self.sql_store.get_recent_notices(limit=limit, category="examination")
            return {"success": True, "data": notices, "error": None}
        except Exception as e:
            return {"success": False, "data": None, "error": {"code": "EXAM_SEARCH_FAILED", "message": str(e)}}

    def search_admission_information(self, query: str, limit: int = 5) -> Dict[str, Any]:
        """
        MCP Tool: search_admission_information
        Retrieves admission circulars, merit lists, and deadlines.
        """
        try:
            notices = self.sql_store.get_recent_notices(limit=limit, category="admission")
            return {"success": True, "data": notices, "error": None}
        except Exception as e:
            return {"success": False, "data": None, "error": {"code": "ADMISSION_SEARCH_FAILED", "message": str(e)}}

    def get_page(self, url: str) -> Dict[str, Any]:
        """
        MCP Tool: get_page
        Retrieves full crawled page record and clean text.
        """
        conn = get_db_connection()
        try:
            cur = conn.execute("SELECT id, url, title, description, clean_text, language, page_type, section, published_date, last_crawled FROM pages WHERE url = ? OR normalized_url = ?", (url, url))
            row = cur.fetchone()
            if not row:
                return {"success": False, "data": None, "error": {"code": "PAGE_NOT_FOUND", "message": f"Page {url} not found."}}
            return {"success": True, "data": dict(row), "error": None}
        except Exception as e:
            return {"success": False, "data": None, "error": {"code": "PAGE_FETCH_FAILED", "message": str(e)}}
        finally:
            conn.close()

_knowledge_mcp_server_instance: Optional[KnowledgeMCPServer] = None

def get_knowledge_mcp_server() -> KnowledgeMCPServer:
    global _knowledge_mcp_server_instance
    if _knowledge_mcp_server_instance is None:
        _knowledge_mcp_server_instance = KnowledgeMCPServer()
    return _knowledge_mcp_server_instance
