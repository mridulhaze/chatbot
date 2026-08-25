import os
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional

from backend.crawler.db import get_db_connection

logger = logging.getLogger("NU_DOCUMENT_MCP_SERVER")

class DocumentMCPServer:
    """
    Official MCP Server for National University Document & Form Retrieval (PDF, DOCX, XLSX, TXT).
    """
    def search_documents(self, query: str, file_type: Optional[str] = None, limit: int = 5) -> Dict[str, Any]:
        """
        MCP Tool: search_documents
        Locates official forms, circulars, syllabi, guidelines, and notices from database.
        """
        conn = get_db_connection()
        try:
            sql = "SELECT id, url, title, file_name, mime_type, file_size, document_type, section, downloaded_at FROM documents WHERE active = 1"
            params = []
            if query:
                sql += " AND (title LIKE ? OR file_name LIKE ? OR extracted_text LIKE ?)"
                q_param = f"%{query}%"
                params.extend([q_param, q_param, q_param])
            if file_type:
                sql += " AND document_type = ?"
                params.append(file_type.upper())
            sql += " ORDER BY id DESC LIMIT ?"
            params.append(limit)

            cur = conn.execute(sql, params)
            results = [dict(r) for r in cur.fetchall()]
            return {"success": True, "data": results, "error": None}
        except Exception as e:
            logger.error(f"MCP search_documents error: {e}", exc_info=True)
            return {"success": False, "data": None, "error": {"code": "DOC_SEARCH_FAILED", "message": str(e)}}
        finally:
            conn.close()

    def get_document_text(self, url_or_id: str) -> Dict[str, Any]:
        """
        MCP Tool: get_document_text
        Extracts plain text and page information from document.
        """
        conn = get_db_connection()
        try:
            cur = conn.execute("SELECT id, url, title, file_name, extracted_text, page_count, document_type, downloaded_at FROM documents WHERE url = ? OR id = ?", (url_or_id, url_or_id))
            row = cur.fetchone()
            if not row:
                return {"success": False, "data": None, "error": {"code": "DOC_NOT_FOUND", "message": f"Document {url_or_id} not found."}}
            return {"success": True, "data": dict(row), "error": None}
        except Exception as e:
            return {"success": False, "data": None, "error": {"code": "DOC_TEXT_FAILED", "message": str(e)}}
        finally:
            conn.close()

    def get_document_metadata(self, url_or_id: str) -> Dict[str, Any]:
        """
        MCP Tool: get_document_metadata
        Returns file statistics and checksum metadata.
        """
        conn = get_db_connection()
        try:
            cur = conn.execute("SELECT id, url, file_name, mime_type, file_size, content_hash, page_count, document_type, section, downloaded_at FROM documents WHERE url = ? OR id = ?", (url_or_id, url_or_id))
            row = cur.fetchone()
            if not row:
                return {"success": False, "data": None, "error": {"code": "DOC_NOT_FOUND", "message": f"Document {url_or_id} not found."}}
            return {"success": True, "data": dict(row), "error": None}
        except Exception as e:
            return {"success": False, "data": None, "error": {"code": "DOC_META_FAILED", "message": str(e)}}
        finally:
            conn.close()

_document_mcp_server_instance: Optional[DocumentMCPServer] = None

def get_document_mcp_server() -> DocumentMCPServer:
    global _document_mcp_server_instance
    if _document_mcp_server_instance is None:
        _document_mcp_server_instance = DocumentMCPServer()
    return _document_mcp_server_instance
