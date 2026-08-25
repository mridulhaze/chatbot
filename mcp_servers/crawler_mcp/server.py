import asyncio
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

from backend.crawler.deep_crawler import DeepCrawlerController, get_crawler_instance
from backend.crawler.site_map import generate_website_map
from backend.crawler.db import get_db_connection

logger = logging.getLogger("NU_CRAWLER_MCP")

class CrawlerMCPServer:
    """
    Model Context Protocol (MCP) Server for National University Intelligent Web Crawler.
    Provides typed, controlled tools for crawling, monitoring, pausing, website map inspection, and retries.
    """
    def __init__(self):
        self.name = "nu_crawler_mcp"
        self.version = "2.0.0"
        self._current_task: Optional[asyncio.Task] = None

    def start_crawl(self, start_url: str = "https://www.nu.ac.bd/", max_pages: int = 100, max_depth: int = 15, concurrency: int = 5) -> Dict[str, Any]:
        """Starts a background asynchronous deep crawl job across the NU domain."""
        crawler = get_crawler_instance()
        if crawler.is_running:
            return {"status": "busy", "job_id": crawler.job_id, "message": "A crawl job is already running."}

        crawler.start_url = start_url
        crawler.max_pages = max_pages
        crawler.max_depth = max_depth
        crawler.concurrency = concurrency
        crawler.job_id = f"CRAWL-{datetime.utcnow().strftime('%Y%m%d-%H%M%S')}"

        # Run in background event loop
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        self._current_task = loop.create_task(crawler.run_crawl_async())

        return {
            "status": "started",
            "job_id": crawler.job_id,
            "start_url": start_url,
            "max_pages": max_pages,
            "message": f"Deep crawler started for {start_url}"
        }

    def crawl_status(self, job_id: Optional[str] = None) -> Dict[str, Any]:
        """Returns the live status, progress metrics, and error stats of the crawler."""
        crawler = get_crawler_instance()
        conn = get_db_connection()
        try:
            if job_id:
                cur = conn.execute("SELECT * FROM crawl_jobs WHERE job_id = ?", (job_id,))
            else:
                cur = conn.execute("SELECT * FROM crawl_jobs ORDER BY id DESC LIMIT 1")
            job_row = cur.fetchone()

            # Query live counts
            counts_cur = conn.execute("SELECT status, COUNT(*) as c FROM crawl_urls GROUP BY status")
            queue_counts = {r["status"]: r["c"] for r in counts_cur.fetchall()}

            total_pages = conn.execute("SELECT COUNT(*) as c FROM pages WHERE active = 1").fetchone()["c"]
            total_docs = conn.execute("SELECT COUNT(*) as c FROM documents WHERE active = 1").fetchone()["c"]

            return {
                "is_running": crawler.is_running,
                "is_paused": crawler.is_paused,
                "current_job": dict(job_row) if job_row else None,
                "queue_counts": queue_counts,
                "total_indexed_pages": total_pages,
                "total_indexed_documents": total_docs
            }
        finally:
            conn.close()

    def pause_crawl(self) -> Dict[str, Any]:
        """Pauses the active crawl loop."""
        crawler = get_crawler_instance()
        if not crawler.is_running:
            return {"status": "idle", "message": "No crawler is currently running."}
        crawler.is_paused = True
        return {"status": "paused", "job_id": crawler.job_id, "message": "Crawler paused."}

    def resume_crawl(self) -> Dict[str, Any]:
        """Resumes a paused crawl loop."""
        crawler = get_crawler_instance()
        if not crawler.is_running:
            return {"status": "idle", "message": "No crawler is currently running."}
        crawler.is_paused = False
        return {"status": "running", "job_id": crawler.job_id, "message": "Crawler resumed."}

    def stop_crawl(self) -> Dict[str, Any]:
        """Stops the active crawler."""
        crawler = get_crawler_instance()
        if not crawler.is_running:
            return {"status": "idle", "message": "No crawler is running."}
        crawler.stop_requested = True
        return {"status": "stopping", "job_id": crawler.job_id, "message": "Stop signal sent to crawler."}

    def retry_failed_urls(self) -> Dict[str, Any]:
        """Re-queues all errored URLs for retry."""
        conn = get_db_connection()
        try:
            with conn:
                cur = conn.execute("UPDATE crawl_urls SET status = 'queued', error_message = NULL WHERE status = 'error'")
                count = cur.rowcount
            return {"status": "success", "requeued_count": count, "message": f"Re-queued {count} failed URLs."}
        finally:
            conn.close()

    def get_website_map(self) -> Dict[str, Any]:
        """Retrieves the complete hierarchical website structure map."""
        return generate_website_map()

    def get_crawl_statistics(self) -> Dict[str, Any]:
        """Returns aggregated metrics on pages, documents, sections, and errors."""
        conn = get_db_connection()
        try:
            total_pages = conn.execute("SELECT COUNT(*) as c FROM pages").fetchone()["c"]
            total_docs = conn.execute("SELECT COUNT(*) as c FROM documents").fetchone()["c"]
            total_chunks = conn.execute("SELECT COUNT(*) as c FROM knowledge_chunks").fetchone()["c"]
            recent_errors = conn.execute("SELECT url, error_message, created_at FROM crawl_errors ORDER BY id DESC LIMIT 10").fetchall()
            return {
                "total_pages": total_pages,
                "total_documents": total_docs,
                "total_knowledge_chunks": total_chunks,
                "recent_errors": [dict(r) for r in recent_errors]
            }
        finally:
            conn.close()

_crawler_mcp_instance: Optional[CrawlerMCPServer] = None

def get_crawler_mcp_server() -> CrawlerMCPServer:
    global _crawler_mcp_instance
    if _crawler_mcp_instance is None:
        _crawler_mcp_instance = CrawlerMCPServer()
    return _crawler_mcp_instance
