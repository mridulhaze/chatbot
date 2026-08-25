import json
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone

from .db import get_db_connection

logger = logging.getLogger("NU_SITE_MAP")

def generate_website_map() -> Dict[str, Any]:
    """
    Generates a structured, hierarchical website map of the National University ecosystem,
    grouped by core sections (Notices, Admission, Examination, Results, Documents, etc.)
    with node metrics, child relationships, document counts, and health statuses.
    """
    conn = get_db_connection()
    try:
        # 1. Fetch all configured sections
        cur = conn.execute("SELECT * FROM website_sections ORDER BY priority DESC")
        sections = [dict(r) for r in cur.fetchall()]

        # 2. Fetch all active pages
        cur_p = conn.execute("""
            SELECT id, url, normalized_url, title, section, page_type, parent_url, published_date, last_crawled, active
            FROM pages
            WHERE active = 1
            ORDER BY id ASC
        """)
        pages = [dict(r) for r in cur_p.fetchall()]

        # 3. Fetch all active documents
        cur_d = conn.execute("""
            SELECT id, url, normalized_url, title, file_name, mime_type, file_size, document_type, section, parent_url, downloaded_at, active
            FROM documents
            WHERE active = 1
            ORDER BY id ASC
        """)
        documents = [dict(r) for r in cur_d.fetchall()]

        # 4. Fetch error count
        error_count = conn.execute("SELECT COUNT(*) as c FROM crawl_errors").fetchone()["c"]

        # Build Section Nodes
        section_nodes: Dict[str, Dict[str, Any]] = {}
        for s in sections:
            s_name = s["name"]
            section_nodes[s_name] = {
                "section": s_name,
                "name_bn": s.get("name_bn") or s_name,
                "url": s.get("url"),
                "priority": s.get("priority", 50),
                "total_pages": 0,
                "total_documents": 0,
                "last_crawled": None,
                "pages": [],
                "documents": []
            }

        # Populate pages into sections
        for p in pages:
            sec = p.get("section") or "General"
            if sec not in section_nodes:
                section_nodes[sec] = {
                    "section": sec,
                    "name_bn": sec,
                    "url": p["url"],
                    "priority": 40,
                    "total_pages": 0,
                    "total_documents": 0,
                    "last_crawled": None,
                    "pages": [],
                    "documents": []
                }
            section_nodes[sec]["pages"].append({
                "id": p["id"],
                "url": p["url"],
                "title": p.get("title") or p["url"],
                "page_type": p.get("page_type"),
                "published_date": p.get("published_date"),
                "last_crawled": p.get("last_crawled")
            })
            section_nodes[sec]["total_pages"] += 1
            if p.get("last_crawled"):
                if not section_nodes[sec]["last_crawled"] or p["last_crawled"] > section_nodes[sec]["last_crawled"]:
                    section_nodes[sec]["last_crawled"] = p["last_crawled"]

        # Populate documents into sections
        for d in documents:
            sec = d.get("section") or "Documents"
            if sec not in section_nodes:
                section_nodes[sec] = {
                    "section": sec,
                    "name_bn": sec,
                    "url": d["url"],
                    "priority": 85,
                    "total_pages": 0,
                    "total_documents": 0,
                    "last_crawled": None,
                    "pages": [],
                    "documents": []
                }
            section_nodes[sec]["documents"].append({
                "id": d["id"],
                "url": d["url"],
                "file_name": d.get("file_name"),
                "document_type": d.get("document_type"),
                "file_size_kb": round(d.get("file_size", 0) / 1024, 1),
                "downloaded_at": d.get("downloaded_at")
            })
            section_nodes[sec]["total_documents"] += 1

        tree = list(section_nodes.values())
        tree.sort(key=lambda x: x["priority"], reverse=True)

        total_pages = len(pages)
        total_docs = len(documents)

        health = "🟢 Healthy"
        if error_count > 50:
            health = "🟡 Warning"
        if error_count > 200:
            health = "🔴 Critical"

        return {
            "root_url": "https://www.nu.ac.bd/",
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "total_sections": len(tree),
            "total_pages": total_pages,
            "total_documents": total_docs,
            "total_errors": error_count,
            "health": health,
            "sections": tree
        }
    finally:
        conn.close()
