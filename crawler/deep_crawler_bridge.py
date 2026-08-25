import os
import asyncio
import logging
import threading
from typing import Dict, Any, Optional
from datetime import datetime

from backend.crawler.deep_crawler import DeepCrawlerController, get_crawler_instance
from backend.crawler.site_map import generate_website_map
from backend.crawler.db import get_db_connection
from db.sql_store import get_sql_store

logger = logging.getLogger("NU_DEEP_CRAWLER_BRIDGE")

def run_deep_crawler(max_pages: int = 60, delay_seconds: float = 0.3) -> Dict[str, Any]:
    """
    Spawns the asynchronous intelligent Deep Crawler worker thread,
    traversing internal links, extracting PDF documents, and synchronizing with ChromaDB.
    """
    crawler = get_crawler_instance()
    if crawler.is_running:
        return {"status": "busy", "message": "Deep crawler is already running in background."}

    crawler.max_pages = max_pages
    crawler.delay_seconds = delay_seconds

    sql_store = get_sql_store()
    log_id = sql_store.start_crawl_log(f"Deep Intelligent Crawler (max_pages={max_pages})")

    def _worker_thread():
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(crawler.run_crawl_async())
            loop.close()

            sql_store.finish_crawl_log(
                log_id=log_id,
                status=result.get("status", "completed"),
                pages_scraped=result.get("processed_urls", 0),
                new_items=result.get("documents_count", 0),
                errors=""
            )
        except Exception as e:
            logger.error(f"Deep crawler thread error: {e}", exc_info=True)
            sql_store.finish_crawl_log(
                log_id=log_id,
                status="failed",
                pages_scraped=0,
                new_items=0,
                errors=str(e)
            )

    t = threading.Thread(target=_worker_thread, daemon=True)
    t.start()

    return {
        "status": "started",
        "job_id": crawler.job_id,
        "max_pages": max_pages,
        "message": "Deep intelligent crawler launched in background!"
    }

def get_deep_crawler_status() -> Dict[str, Any]:
    crawler = get_crawler_instance()
    conn = get_db_connection()
    try:
        cur = conn.execute("SELECT * FROM crawl_jobs ORDER BY id DESC LIMIT 1")
        job = cur.fetchone()

        pages_count = conn.execute("SELECT COUNT(*) as c FROM pages WHERE active = 1").fetchone()["c"]
        docs_count = conn.execute("SELECT COUNT(*) as c FROM documents WHERE active = 1").fetchone()["c"]
        chunks_count = conn.execute("SELECT COUNT(*) as c FROM knowledge_chunks WHERE active = 1").fetchone()["c"]

        return {
            "is_running": crawler.is_running,
            "is_paused": crawler.is_paused,
            "last_status": "running" if crawler.is_running else (dict(job)["status"] if job else "idle"),
            "pages_crawled": pages_count,
            "documents_extracted": docs_count,
            "chunks_indexed": chunks_count,
            "last_run": dict(job)["started_at"] if job else None,
            "current_job": dict(job) if job else None
        }
    finally:
        conn.close()

def get_site_map_data() -> Dict[str, Any]:
    return generate_website_map()
