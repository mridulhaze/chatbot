import os
import re
import json
import time
import sqlite3
import asyncio
import logging
import urllib.robotparser
from pathlib import Path
from typing import Dict, Any, List, Optional, Set, Tuple
from datetime import datetime
from urllib.parse import urlparse

import httpx
from langchain_core.documents import Document

from .db import get_db_connection
from .extractors import (
    normalize_url,
    compute_sha256,
    clean_extracted_text,
    extract_html_page,
    extract_document_file,
    classify_content
)
from db.vector_store import get_vector_store
from db.sql_store import get_sql_store

logger = logging.getLogger("NU_DEEP_CRAWLER")

ALLOWED_HOSTS = {
    "www.nu.ac.bd", "nu.ac.bd", "results.nu.ac.bd", "app1.nu.edu.bd",
    "app.nu.edu.bd", "services.nu.edu.bd", "ems.nu.ac.bd", "exam.nu.ac.bd"
}

DOCUMENT_EXTENSIONS = {".pdf", ".docx", ".doc", ".xlsx", ".xls", ".csv", ".txt"}

class DeepCrawlerController:
    """
    Intelligent, resumable, concurrent Deep Crawler for National University (NU).
    Features priority queueing, content hashing, incremental vector store sync,
    document extraction (PDF/DOCX/XLSX), and resilient robots policy.
    """
    def __init__(
        self,
        start_url: str = "https://www.nu.ac.bd/",
        max_pages: int = 100,
        max_depth: int = 15,
        concurrency: int = 5,
        delay_seconds: float = 0.3,
        download_documents: bool = True
    ):
        self.start_url = normalize_url(start_url)
        self.max_pages = max_pages
        self.max_depth = max_depth
        self.concurrency = concurrency
        self.delay_seconds = delay_seconds
        self.download_documents = download_documents

        self.job_id = f"CRAWL-{datetime.utcnow().strftime('%Y%m%d-%H%M%S')}"
        self.is_running = False
        self.is_paused = False
        self.stop_requested = False

        self.robot_parsers: Dict[str, Optional[urllib.robotparser.RobotFileParser]] = {}
        self.vector_store = get_vector_store()
        self.sql_store = get_sql_store()

    def _get_robot_parser(self, origin: str) -> Optional[urllib.robotparser.RobotFileParser]:
        if origin in self.robot_parsers:
            return self.robot_parsers[origin]
        
        rp = urllib.robotparser.RobotFileParser()
        try:
            robots_url = f"{origin}/robots.txt"
            with httpx.Client(timeout=6.0, verify=False) as client:
                resp = client.get(robots_url)
                if resp.status_code == 200 and not resp.text.strip().startswith("<!DOCTYPE"):
                    rp.parse(resp.text.splitlines())
                    self.robot_parsers[origin] = rp
                    return rp
        except Exception:
            pass

        self.robot_parsers[origin] = None
        return None

    def is_url_allowed(self, url: str) -> bool:
        if not url:
            return False
        parsed = urlparse(url)
        host = parsed.netloc.lower().split(":")[0]
        if host not in ALLOWED_HOSTS and not host.endswith(".nu.ac.bd") and not host.endswith(".nu.edu.bd"):
            return False

        # Whitelist vital document directories even if aggressive robots disallows /uploads/
        path_lower = parsed.path.lower()
        if any(path_lower.startswith(p) for p in ["/uploads/", "/syllabus/", "/recent-notices.php", "/notice"]):
            return True

        origin = f"{parsed.scheme}://{parsed.netloc}"
        rp = self._get_robot_parser(origin)
        if rp:
            try:
                return rp.can_fetch("NU-Academic-Crawler", url)
            except Exception:
                return True
        return True

    def init_crawl_job(self):
        conn = get_db_connection()
        try:
            now_str = datetime.utcnow().isoformat()
            config_json = json.dumps({
                "start_url": self.start_url,
                "max_pages": self.max_pages,
                "max_depth": self.max_depth,
                "concurrency": self.concurrency,
                "delay_seconds": self.delay_seconds
            })
            with conn:
                conn.execute("""
                    INSERT INTO crawl_jobs (job_id, start_url, status, started_at, config_json)
                    VALUES (?, ?, 'running', ?, ?)
                """, (self.job_id, self.start_url, now_str, config_json))

                # Seed start URL
                conn.execute("""
                    INSERT OR IGNORE INTO crawl_urls (url, normalized_url, status, priority, first_seen)
                    VALUES (?, ?, 'queued', 100, ?)
                """, (self.start_url, self.start_url, now_str))
        finally:
            conn.close()

    async def run_crawl_async(self) -> Dict[str, Any]:
        self.is_running = True
        self.is_paused = False
        self.stop_requested = False
        self.init_crawl_job()

        logger.info(f"Starting Deep Crawler Job {self.job_id} on {self.start_url} (Max Pages: {self.max_pages})...")

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36 (NU Academic Knowledge Ingest)",
            "Accept-Language": "bn,en;q=0.9"
        }

        limits = httpx.Limits(max_keepalive_connections=15, max_connections=20)
        timeout = httpx.Timeout(25.0, connect=10.0)

        processed_count = 0
        new_count = 0
        changed_count = 0
        docs_count = 0
        chunks_count = 0

        async with httpx.AsyncClient(headers=headers, limits=limits, timeout=timeout, verify=False, follow_redirects=True) as client:
            while processed_count < self.max_pages and not self.stop_requested:
                if self.is_paused:
                    await asyncio.sleep(1.0)
                    continue

                # 1. Fetch batch of queued URLs by priority
                batch = self._get_queued_urls_batch(limit=self.concurrency)
                if not batch:
                    logger.info("Crawl queue is empty. Crawl job completed successfully.")
                    break

                # 2. Process batch concurrently
                tasks = [self._process_single_url(client, item) for item in batch]
                results = await asyncio.gather(*tasks, return_exceptions=True)

                for res in results:
                    if isinstance(res, dict) and res.get("success"):
                        processed_count += 1
                        if res.get("is_new"):
                            new_count += 1
                        if res.get("is_changed"):
                            changed_count += 1
                        if res.get("is_document"):
                            docs_count += 1
                        chunks_count += res.get("chunks_created", 0)

                await asyncio.sleep(self.delay_seconds)

        self.is_running = False
        status_final = "stopped" if self.stop_requested else "completed"
        self._finish_crawl_job(status_final, processed_count, new_count, changed_count, docs_count, chunks_count)

        logger.info(f"Deep Crawler Job {self.job_id} finished: Processed {processed_count} pages/docs, New: {new_count}, Changed: {changed_count}, Chunks Indexed: {chunks_count}.")
        return {
            "job_id": self.job_id,
            "status": status_final,
            "processed_urls": processed_count,
            "new_urls": new_count,
            "changed_urls": changed_count,
            "documents_count": docs_count,
            "chunks_indexed": chunks_count
        }

    def _get_queued_urls_batch(self, limit: int = 5) -> List[Dict[str, Any]]:
        conn = get_db_connection()
        try:
            cur = conn.execute("""
                SELECT id, url, normalized_url, parent_url, depth, priority, retry_count
                FROM crawl_urls
                WHERE status = 'queued'
                ORDER BY priority DESC, retry_count ASC, id ASC
                LIMIT ?
            """, (limit,))
            rows = [dict(r) for r in cur.fetchall()]
            if rows:
                ids = [r["id"] for r in rows]
                placeholders = ",".join("?" for _ in ids)
                with conn:
                    conn.execute(f"UPDATE crawl_urls SET status = 'processing' WHERE id IN ({placeholders})", ids)
            return rows
        finally:
            conn.close()

    async def _process_single_url(self, client: httpx.AsyncClient, item: Dict[str, Any]) -> Dict[str, Any]:
        url = item["url"]
        depth = item["depth"]
        now_str = datetime.utcnow().isoformat()

        if not self.is_url_allowed(url):
            self._update_url_status(url, status="skipped", error="Disallowed by domain scope")
            return {"success": False}

        try:
            resp = await client.get(url)
            http_status = resp.status_code
            content_type = resp.headers.get("Content-Type", "").lower()
            raw_bytes = resp.content

            if http_status != 200:
                self._update_url_status(url, status="error", http_status=http_status, error=f"HTTP {http_status}")
                return {"success": False}

            # Check if Document (PDF, DOCX, XLSX, etc.)
            parsed_path = urlparse(url).path.lower()
            is_doc = any(parsed_path.endswith(ext) for ext in DOCUMENT_EXTENSIONS) or "application/pdf" in content_type or "wordprocessingml" in content_type

            if is_doc:
                return await self._handle_document(url, raw_bytes, content_type, depth, item.get("parent_url"), now_str)
            else:
                return await self._handle_web_page(url, resp.text, depth, item.get("parent_url"), now_str)

        except Exception as e:
            err_msg = str(e)
            logger.warning(f"Failed to fetch {url}: {err_msg}")
            self._update_url_status(url, status="error", error=err_msg, increment_retry=True)
            return {"success": False}

    async def _handle_web_page(self, url: str, html_text: str, depth: int, parent_url: Optional[str], now_str: str) -> Dict[str, Any]:
        parsed = extract_html_page(html_text, url)
        content_hash = parsed["content_hash"]
        clean_text = parsed["clean_text"]

        conn = get_db_connection()
        is_new = False
        is_changed = False
        chunks_created = 0

        try:
            # Check existing hash
            cur = conn.execute("SELECT id, content_hash FROM pages WHERE url = ?", (url,))
            existing = cur.fetchone()

            if not existing:
                is_new = True
                with conn:
                    conn.execute("""
                        INSERT INTO pages (url, normalized_url, title, description, content, clean_text, language, page_type, section, parent_url, content_hash, published_date, first_crawled, last_crawled, active)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1)
                    """, (
                        url, url, parsed["title"], parsed["description"], html_text[:50000], clean_text,
                        parsed["language"], parsed["page_type"], parsed["section"], parent_url,
                        content_hash, parsed["published_date"], now_str, now_str
                    ))
            elif existing["content_hash"] != content_hash:
                is_changed = True
                with conn:
                    conn.execute("""
                        UPDATE pages SET
                            title = ?, description = ?, clean_text = ?, content = ?,
                            page_type = ?, section = ?, content_hash = ?, published_date = ?,
                            last_modified = ?, last_crawled = ?, active = 1
                        WHERE url = ?
                    """, (
                        parsed["title"], parsed["description"], clean_text, html_text[:50000],
                        parsed["page_type"], parsed["section"], content_hash, parsed["published_date"],
                        now_str, now_str, url
                    ))
            else:
                # Unchanged
                with conn:
                    conn.execute("UPDATE pages SET last_crawled = ? WHERE url = ?", (now_str, url))

            # Sync to ChromaDB Vector Store if new or changed
            if (is_new or is_changed) and len(clean_text) > 50:
                doc_meta = {
                    "source": url,
                    "title": parsed["title"][:120],
                    "category": parsed["section"],
                    "page_type": parsed["page_type"],
                    "published_date": parsed["published_date"] or "N/A",
                    "type": "crawled_page"
                }
                rag_content = f"# {parsed['title']}\nSection: {parsed['section']}\nURL: {url}\nDate: {parsed['published_date'] or 'N/A'}\n\n{clean_text}"
                doc = Document(page_content=rag_content, metadata=doc_meta)
                chunks_created = self.vector_store.split_and_add_documents([doc])

                # Also insert into notice table if notice category
                if parsed["page_type"] in ["NOTICE", "EXAMINATION", "ADMISSION"]:
                    self.sql_store.upsert_notice(
                        title=parsed["title"],
                        url=url,
                        pdf_url=None,
                        category=parsed["section"],
                        published_date=parsed["published_date"] or "N/A",
                        raw_text=clean_text[:1500]
                    )

            # Discover and queue internal sub-links
            if depth < self.max_depth:
                self._enqueue_discovered_links(conn, url, parsed["links"], depth + 1)

            self._update_url_status(url, status="done", http_status=200, content_type="text/html", content_hash=content_hash, page_type=parsed["page_type"], section=parsed["section"])

            return {
                "success": True,
                "is_new": is_new,
                "is_changed": is_changed,
                "is_document": False,
                "chunks_created": chunks_created
            }
        finally:
            conn.close()

    async def _handle_document(self, url: str, raw_bytes: bytes, content_type: str, depth: int, parent_url: Optional[str], now_str: str) -> Dict[str, Any]:
        parsed = extract_document_file(raw_bytes, url, content_type)
        content_hash = parsed["content_hash"]
        extracted_text = parsed["extracted_text"]

        conn = get_db_connection()
        is_new = False
        is_changed = False
        chunks_created = 0

        try:
            cur = conn.execute("SELECT id, content_hash FROM documents WHERE url = ?", (url,))
            existing = cur.fetchone()

            if not existing:
                is_new = True
                with conn:
                    conn.execute("""
                        INSERT INTO documents (url, normalized_url, title, file_name, mime_type, file_size, content_hash, extracted_text, page_count, document_type, section, parent_url, downloaded_at, last_updated, active)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1)
                    """, (
                        url, url, parsed["file_name"], parsed["file_name"], content_type,
                        parsed["file_size"], content_hash, extracted_text, parsed["page_count"],
                        parsed["document_type"], parsed["section"], parent_url, now_str, now_str
                    ))
            elif existing["content_hash"] != content_hash:
                is_changed = True
                with conn:
                    conn.execute("""
                        UPDATE documents SET
                            extracted_text = ?, content_hash = ?, page_count = ?,
                            last_updated = ?, active = 1
                        WHERE url = ?
                    """, (extracted_text, content_hash, parsed["page_count"], now_str, url))
            else:
                with conn:
                    conn.execute("UPDATE documents SET last_updated = ? WHERE url = ?", (now_str, url))

            # Sync extracted document text into ChromaDB
            if (is_new or is_changed) and len(extracted_text) > 40:
                doc_meta = {
                    "source": url,
                    "title": parsed["file_name"][:120],
                    "category": parsed["section"],
                    "document_type": parsed["document_type"],
                    "published_date": parsed["published_date"] or "N/A",
                    "type": "official_document"
                }
                doc_content = f"# National University Official Document: {parsed['file_name']}\nType: {parsed['document_type']}\nURL: {url}\n\n{extracted_text}"
                doc = Document(page_content=doc_content, metadata=doc_meta)
                chunks_created = self.vector_store.split_and_add_documents([doc])

            self._update_url_status(url, status="done", http_status=200, content_type=content_type or "application/pdf", content_hash=content_hash, page_type="DOCUMENT", section=parsed["section"])

            return {
                "success": True,
                "is_new": is_new,
                "is_changed": is_changed,
                "is_document": True,
                "chunks_created": chunks_created
            }
        finally:
            conn.close()

    def _enqueue_discovered_links(self, conn: sqlite3.Connection, source_url: str, links: List[Dict[str, str]], next_depth: int):
        now_str = datetime.utcnow().isoformat()
        with conn:
            for l in links:
                target = l["url"]
                text = l.get("text", "")
                if not self.is_url_allowed(target):
                    continue

                # Add link record
                conn.execute("""
                    INSERT OR IGNORE INTO page_links (source_url, target_url, link_text, relation, discovered_at)
                    VALUES (?, ?, ?, 'internal', ?)
                """, (source_url, target, text[:400], now_str))

                # Calculate priority score
                section, page_type, priority = classify_content(target, text, "")

                conn.execute("""
                    INSERT OR IGNORE INTO crawl_urls (url, normalized_url, parent_url, depth, status, priority, first_seen)
                    VALUES (?, ?, ?, ?, 'queued', ?, ?)
                """, (target, target, source_url, next_depth, priority, now_str))

    def _update_url_status(
        self,
        url: str,
        status: str,
        http_status: Optional[int] = None,
        content_type: Optional[str] = None,
        content_hash: Optional[str] = None,
        page_type: Optional[str] = None,
        section: Optional[str] = None,
        error: Optional[str] = None,
        increment_retry: bool = False
    ):
        conn = get_db_connection()
        try:
            now_str = datetime.utcnow().isoformat()
            with conn:
                retry_clause = "retry_count = retry_count + 1," if increment_retry else ""
                conn.execute(f"""
                    UPDATE crawl_urls SET
                        status = ?, http_status = COALESCE(?, http_status),
                        content_type = COALESCE(?, content_type),
                        content_hash = COALESCE(?, content_hash),
                        page_type = COALESCE(?, page_type),
                        section = COALESCE(?, section),
                        error_message = ?, {retry_clause}
                        last_crawled = ?
                    WHERE url = ?
                """, (status, http_status, content_type, content_hash, page_type, section, error, now_str, url))

                if error:
                    conn.execute("""
                        INSERT INTO crawl_errors (job_id, url, error_type, error_message, http_status, created_at)
                        VALUES (?, ?, 'FETCH_ERROR', ?, ?, ?)
                    """, (self.job_id, url, error, http_status, now_str))
        finally:
            conn.close()

    def _finish_crawl_job(self, status: str, processed: int, new_u: int, changed_u: int, docs: int, chunks: int):
        conn = get_db_connection()
        try:
            now_str = datetime.utcnow().isoformat()
            with conn:
                conn.execute("""
                    UPDATE crawl_jobs SET
                        status = ?, completed_at = ?, processed_urls = ?,
                        new_urls = ?, changed_urls = ?, documents_count = ?, chunks_count = ?
                    WHERE job_id = ?
                """, (status, now_str, processed, new_u, changed_u, docs, chunks, self.job_id))
        finally:
            conn.close()

# Singleton controller instance
_active_crawler_instance: Optional[DeepCrawlerController] = None

def get_crawler_instance() -> DeepCrawlerController:
    global _active_crawler_instance
    if _active_crawler_instance is None:
        _active_crawler_instance = DeepCrawlerController()
    return _active_crawler_instance
