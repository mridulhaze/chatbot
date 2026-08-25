import os
import sqlite3
import hashlib
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime

logger = logging.getLogger("NU_CRAWLER_DB")

DEFAULT_DB_PATH = Path(__file__).resolve().parent.parent.parent / "data" / "nu_deep_crawler.sqlite3"

def get_db_connection(db_path: Optional[str] = None) -> sqlite3.Connection:
    target_path = Path(db_path) if db_path else DEFAULT_DB_PATH
    target_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(target_path), timeout=30.0, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA synchronous=NORMAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn

# Alias for external agents and enrichment services
get_crawler_db = get_db_connection

def init_crawler_db(db_path: Optional[str] = None):
    conn = get_db_connection(db_path)
    with conn:
        conn.executescript("""
        CREATE TABLE IF NOT EXISTS crawl_jobs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            job_id TEXT UNIQUE NOT NULL,
            start_url TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'running', -- running, paused, completed, stopped, failed
            started_at TEXT NOT NULL,
            completed_at TEXT,
            total_urls INTEGER DEFAULT 0,
            processed_urls INTEGER DEFAULT 0,
            failed_urls INTEGER DEFAULT 0,
            new_urls INTEGER DEFAULT 0,
            changed_urls INTEGER DEFAULT 0,
            documents_count INTEGER DEFAULT 0,
            chunks_count INTEGER DEFAULT 0,
            config_json TEXT,
            error_message TEXT
        );

        CREATE TABLE IF NOT EXISTS crawl_urls (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            url TEXT UNIQUE NOT NULL,
            normalized_url TEXT NOT NULL,
            parent_url TEXT,
            depth INTEGER NOT NULL DEFAULT 0,
            status TEXT NOT NULL DEFAULT 'queued', -- queued, processing, done, error, skipped
            priority INTEGER NOT NULL DEFAULT 50, -- 10 (low) to 100 (urgent notices)
            http_status INTEGER,
            content_type TEXT,
            page_type TEXT DEFAULT 'general',
            section TEXT DEFAULT 'General',
            first_seen TEXT NOT NULL,
            last_crawled TEXT,
            last_success TEXT,
            crawl_count INTEGER DEFAULT 0,
            retry_count INTEGER DEFAULT 0,
            content_hash TEXT,
            error_message TEXT
        );

        CREATE TABLE IF NOT EXISTS pages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            url TEXT UNIQUE NOT NULL,
            normalized_url TEXT NOT NULL,
            title TEXT,
            description TEXT,
            content TEXT,
            clean_text TEXT,
            language TEXT DEFAULT 'bn',
            page_type TEXT DEFAULT 'general',
            section TEXT DEFAULT 'General',
            parent_url TEXT,
            content_hash TEXT NOT NULL,
            published_date TEXT,
            last_modified TEXT,
            first_crawled TEXT NOT NULL,
            last_crawled TEXT NOT NULL,
            academic_metadata_json TEXT,
            active INTEGER NOT NULL DEFAULT 1
        );

        CREATE TABLE IF NOT EXISTS documents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            url TEXT UNIQUE NOT NULL,
            normalized_url TEXT NOT NULL,
            title TEXT,
            file_name TEXT,
            mime_type TEXT,
            file_size INTEGER,
            content_hash TEXT NOT NULL,
            extracted_text TEXT,
            page_count INTEGER DEFAULT 1,
            document_type TEXT DEFAULT 'PDF',
            section TEXT DEFAULT 'Documents',
            parent_url TEXT,
            local_path TEXT,
            downloaded_at TEXT NOT NULL,
            last_updated TEXT NOT NULL,
            metadata_json TEXT,
            active INTEGER NOT NULL DEFAULT 1
        );

        CREATE TABLE IF NOT EXISTS page_links (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source_url TEXT NOT NULL,
            target_url TEXT NOT NULL,
            link_text TEXT,
            relation TEXT NOT NULL DEFAULT 'internal', -- internal, subdomain, document, external
            discovered_at TEXT NOT NULL,
            UNIQUE(source_url, target_url, link_text)
        );

        CREATE TABLE IF NOT EXISTS website_sections (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            name_bn TEXT,
            url TEXT,
            parent_section TEXT,
            priority INTEGER DEFAULT 50
        );

        CREATE TABLE IF NOT EXISTS knowledge_chunks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source_type TEXT NOT NULL, -- page, document
            source_id INTEGER NOT NULL,
            source_url TEXT NOT NULL,
            title TEXT,
            category TEXT,
            chunk_index INTEGER NOT NULL,
            chunk_text TEXT NOT NULL,
            chunk_hash TEXT NOT NULL,
            embedding_id TEXT,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            active INTEGER NOT NULL DEFAULT 1,
            UNIQUE(source_url, chunk_index)
        );

        CREATE TABLE IF NOT EXISTS crawl_errors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            job_id TEXT,
            url TEXT NOT NULL,
            error_type TEXT NOT NULL,
            error_message TEXT NOT NULL,
            http_status INTEGER,
            retry_count INTEGER DEFAULT 0,
            created_at TEXT NOT NULL,
            resolved_at TEXT
        );

        -- Indexes for ultra-fast priority queries and lookups
        CREATE INDEX IF NOT EXISTS idx_crawl_urls_queue ON crawl_urls(status, priority DESC, retry_count ASC, id ASC);
        CREATE INDEX IF NOT EXISTS idx_crawl_urls_norm ON crawl_urls(normalized_url);
        CREATE INDEX IF NOT EXISTS idx_pages_url ON pages(url);
        CREATE INDEX IF NOT EXISTS idx_pages_type ON pages(page_type, section);
        CREATE INDEX IF NOT EXISTS idx_pages_hash ON pages(content_hash);
        CREATE INDEX IF NOT EXISTS idx_documents_url ON documents(url);
        CREATE INDEX IF NOT EXISTS idx_documents_hash ON documents(content_hash);
        CREATE INDEX IF NOT EXISTS idx_chunks_source ON knowledge_chunks(source_url, active);
        CREATE INDEX IF NOT EXISTS idx_links_target ON page_links(target_url);
        """)

        # Pre-seed standard website sections
        sections = [
            ("Notices", "সকল নোটিশ ও প্রজ্ঞাপন", "https://www.nu.ac.bd/recent-notices.php", None, 100),
            ("Admission", "ভর্তি সংক্রান্ত তথ্য ও নির্দেশিকা", "http://app1.nu.edu.bd/", None, 95),
            ("Examination", "পরীক্ষা সংক্রান্ত বিজ্ঞপ্তি ও ফরম পূরণ", "https://www.nu.ac.bd/", None, 95),
            ("Results", "পরীক্ষার ফলাফল ও আর্কাইভ", "http://results.nu.ac.bd/", None, 95),
            ("Forms & Syllabi", "ফরম, সিলেবাস ও একাডেমিক রেগুলেশন", "https://www.nu.ac.bd/", None, 90),
            ("Documents", "অফিসিয়াল সার্কুলার ও পিডিএফ ফাইল", "https://www.nu.ac.bd/uploads/", None, 85),
            ("Academic", "একাডেমিক প্রোগ্রাম ও অনুষদ", "https://www.nu.ac.bd/", None, 70),
            ("Administration", "বিশ্ববিদ্যালয় প্রশাসন ও দপ্তরসমূহ", "https://www.nu.ac.bd/", None, 60),
            ("Affiliated Colleges", "অধিভুক্ত কলেজ ও প্রতিষ্ঠানসমূহ", "https://www.nu.ac.bd/", None, 50),
            ("General", "সাধারণ ওয়েবসাইট পেজ", "https://www.nu.ac.bd/", None, 40),
        ]
        for name, name_bn, url, parent, priority in sections:
            conn.execute("""
                INSERT OR IGNORE INTO website_sections (name, name_bn, url, parent_section, priority)
                VALUES (?, ?, ?, ?, ?)
            """, (name, name_bn, url, parent, priority))

    conn.close()

# Auto-initialize database on import
init_crawler_db()
