import os
import sqlite3
import hashlib
from pathlib import Path
from typing import Optional, Any
from datetime import datetime

DEFAULT_DB_PATH = Path(__file__).resolve().parent.parent / "data" / "nu_assistant.db"
SCHEMA_PATH = Path(__file__).resolve().parent / "schema.sql"

class SQLStore:
    def __init__(self, db_path: Optional[str | Path] = None):
        self.db_path = Path(db_path) if db_path else DEFAULT_DB_PATH
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(str(self.db_path), check_same_thread=False)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self):
        """Run schema migrations."""
        if SCHEMA_PATH.exists():
            with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
                schema_sql = f.read()
            with self._get_connection() as conn:
                conn.executescript(schema_sql)

    @staticmethod
    def compute_hash(text: str) -> str:
        return hashlib.md5(text.strip().encode("utf-8")).hexdigest()

    # --- Notices CRUD ---
    def upsert_notice(self, title: str, url: str, pdf_url: Optional[str], category: str, published_date: str, raw_text: str) -> bool:
        """
        Inserts or updates a notice if content has changed.
        Returns True if new/updated, False if unchanged.
        """
        content_hash = self.compute_hash(f"{title}|{published_date}|{raw_text}")
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT content_hash FROM notices WHERE url = ?", (url,))
            row = cursor.fetchone()
            if row:
                if row["content_hash"] == content_hash:
                    return False  # No change
                cursor.execute("""
                    UPDATE notices
                    SET title = ?, pdf_url = ?, category = ?, published_date = ?, content_hash = ?, raw_text = ?, scraped_at = CURRENT_TIMESTAMP
                    WHERE url = ?
                """, (title, pdf_url, category, published_date, content_hash, raw_text, url))
            else:
                cursor.execute("""
                    INSERT INTO notices (title, url, pdf_url, category, published_date, content_hash, raw_text)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (title, url, pdf_url, category, published_date, content_hash, raw_text))
            return True

    def get_recent_notices(self, limit: int = 15, category: Optional[str] = None) -> list[dict[str, Any]]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            if category:
                cursor.execute("""
                    SELECT * FROM notices WHERE category LIKE ? ORDER BY id DESC LIMIT ?
                """, (f"%{category}%", limit))
            else:
                cursor.execute("SELECT * FROM notices ORDER BY id DESC LIMIT ?", (limit,))
            return [dict(row) for row in cursor.fetchall()]

    def search_notices(self, query_terms: list[str], limit: int = 10) -> list[dict[str, Any]]:
        if not query_terms:
            return self.get_recent_notices(limit=limit)
        with self._get_connection() as conn:
            cursor = conn.cursor()
            conditions = " OR ".join(["title LIKE ? OR raw_text LIKE ?" for _ in query_terms])
            params = []
            for term in query_terms:
                params.extend([f"%{term}%", f"%{term}%"])
            params.append(limit)
            cursor.execute(f"SELECT * FROM notices WHERE {conditions} ORDER BY id DESC LIMIT ?", params)
            return [dict(row) for row in cursor.fetchall()]

    # --- Admission Info CRUD ---
    def upsert_admission_info(self, program: str, level: str, eligibility: str, deadline: str, notes: str, source_url: str):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM admission_info WHERE program = ? AND level = ?", (program, level))
            row = cursor.fetchone()
            if row:
                cursor.execute("""
                    UPDATE admission_info
                    SET eligibility = ?, deadline = ?, notes = ?, source_url = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                """, (eligibility, deadline, notes, source_url, row["id"]))
            else:
                cursor.execute("""
                    INSERT INTO admission_info (program, level, eligibility, deadline, notes, source_url)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (program, level, eligibility, deadline, notes, source_url))

    def get_admission_info(self, query: Optional[str] = None) -> list[dict[str, Any]]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            if query:
                cursor.execute("""
                    SELECT * FROM admission_info 
                    WHERE program LIKE ? OR level LIKE ? OR notes LIKE ?
                    ORDER BY id DESC LIMIT 10
                """, (f"%{query}%", f"%{query}%", f"%{query}%"))
            else:
                cursor.execute("SELECT * FROM admission_info ORDER BY id DESC LIMIT 20")
            return [dict(row) for row in cursor.fetchall()]

    # --- FAQ & Self-Learned Entries ---
    def insert_faq_entry(self, question: str, answer: str, source_url: str = "", language: str = "bn", 
                         category: str = "General", confidence: float = 1.0, verified_by_admin: int = 0) -> int:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO faq_entries (question, answer, source_url, language, category, confidence, verified_by_admin)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (question, answer, source_url, language, category, confidence, verified_by_admin))
            return cursor.lastrowid

    def get_faqs(self, verified_only: bool = False, limit: int = 50) -> list[dict[str, Any]]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            if verified_only:
                cursor.execute("SELECT * FROM faq_entries WHERE verified_by_admin = 1 ORDER BY id DESC LIMIT ?", (limit,))
            else:
                cursor.execute("SELECT * FROM faq_entries ORDER BY id DESC LIMIT ?", (limit,))
            return [dict(row) for row in cursor.fetchall()]

    def search_faqs(self, query: str, limit: int = 5) -> list[dict[str, Any]]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM faq_entries 
                WHERE question LIKE ? OR answer LIKE ? 
                ORDER BY verified_by_admin DESC, confidence DESC LIMIT ?
            """, (f"%{query}%", f"%{query}%", limit))
            return [dict(row) for row in cursor.fetchall()]

    # --- Gap Queue (Self-Enrichment) ---
    def log_gap(self, user_query: str, language: str = "bn", session_id: str = "", reason: str = "") -> int:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            # Check if recent identical query exists in pending/researching
            cursor.execute("""
                SELECT id FROM gap_queue 
                WHERE user_query = ? AND status IN ('pending', 'candidate_ready')
            """, (user_query,))
            existing = cursor.fetchone()
            if existing:
                return existing["id"]
            cursor.execute("""
                INSERT INTO gap_queue (user_query, language, session_id, reason, status)
                VALUES (?, ?, ?, ?, 'pending')
            """, (user_query, language, session_id, reason))
            return cursor.lastrowid

    def get_gap_queue(self, status: Optional[str] = None, limit: int = 50) -> list[dict[str, Any]]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            if status:
                cursor.execute("SELECT * FROM gap_queue WHERE status = ? ORDER BY id DESC LIMIT ?", (status, limit))
            else:
                cursor.execute("SELECT * FROM gap_queue ORDER BY id DESC LIMIT ?", (limit,))
            return [dict(row) for row in cursor.fetchall()]

    def update_gap_status(self, gap_id: int, status: str, candidate_answer: Optional[str] = None, confidence: Optional[float] = None):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            resolved_at = datetime.now().isoformat() if status in ("resolved", "rejected") else None
            cursor.execute("""
                UPDATE gap_queue
                SET status = ?, candidate_answer = COALESCE(?, candidate_answer),
                    confidence = COALESCE(?, confidence), resolved_at = ?
                WHERE id = ?
            """, (status, candidate_answer, confidence, resolved_at, gap_id))

    def approve_gap_entry(self, gap_id: int, custom_answer: Optional[str] = None) -> Optional[int]:
        """Approves a candidate gap entry and inserts it into faq_entries as verified."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM gap_queue WHERE id = ?", (gap_id,))
            gap = cursor.fetchone()
            if not gap:
                return None
            
            final_answer = custom_answer or gap["candidate_answer"] or ""
            faq_id = self.insert_faq_entry(
                question=gap["user_query"],
                answer=final_answer,
                source_url="https://www.nu.ac.bd",
                language=gap["language"] or "bn",
                category="Self-Enriched FAQ",
                confidence=1.0,
                verified_by_admin=1
            )
            self.update_gap_status(gap_id, status="resolved", candidate_answer=final_answer, confidence=1.0)
            return faq_id

    # --- Crawl Logs ---
    def start_crawl_log(self, source: str) -> int:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO crawl_log (source, status, started_at)
                VALUES (?, 'running', CURRENT_TIMESTAMP)
            """, (source,))
            return cursor.lastrowid

    def finish_crawl_log(self, log_id: int, status: str, pages_scraped: int, new_items: int, errors: str = ""):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE crawl_log
                SET status = ?, finished_at = CURRENT_TIMESTAMP, pages_scraped = ?, new_items = ?, errors = ?
                WHERE id = ?
            """, (status, pages_scraped, new_items, errors, log_id))

    # --- Officers & Employee Directory CRUD ---
    def upsert_officer(self, department_slug: str, department_name: str, department_url: str,
                       name: str, designation_bn: str, designation_en: str,
                       phone: str = "", email: str = "", raw_details: str = "") -> int:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id FROM officers_directory 
                WHERE department_slug = ? AND name = ?
            """, (department_slug, name))
            row = cursor.fetchone()
            if row:
                cursor.execute("""
                    UPDATE officers_directory
                    SET department_name = ?, department_url = ?, designation_bn = ?,
                        designation_en = ?, phone = ?, email = ?, raw_details = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                """, (department_name, department_url, designation_bn, designation_en, phone, email, raw_details, row["id"]))
                return row["id"]
            else:
                cursor.execute("""
                    INSERT INTO officers_directory (department_slug, department_name, department_url, name, designation_bn, designation_en, phone, email, raw_details)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (department_slug, department_name, department_url, name, designation_bn, designation_en, phone, email, raw_details))
                return cursor.lastrowid

    def search_officers(self, query: str, limit: int = 20) -> list[dict[str, Any]]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            pattern = f"%{query.strip()}%"
            cursor.execute("""
                SELECT * FROM officers_directory
                WHERE name LIKE ? 
                   OR designation_bn LIKE ? 
                   OR designation_en LIKE ? 
                   OR email LIKE ?
                   OR phone LIKE ?
                   OR department_name LIKE ?
                   OR department_slug LIKE ?
                ORDER BY id ASC LIMIT ?
            """, (pattern, pattern, pattern, pattern, pattern, pattern, pattern, limit))
            return [dict(row) for row in cursor.fetchall()]

    def get_officers_by_department(self, department_slug: str) -> list[dict[str, Any]]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM officers_directory
                WHERE department_slug = ? OR department_name LIKE ?
                ORDER BY id ASC
            """, (department_slug, f"%{department_slug}%"))
            return [dict(row) for row in cursor.fetchall()]

    def get_all_departments_summary(self) -> list[dict[str, Any]]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT department_slug, department_name, department_url, COUNT(*) as officer_count, MAX(updated_at) as last_updated
                FROM officers_directory
                GROUP BY department_slug
                ORDER BY department_name ASC
            """)
            return [dict(row) for row in cursor.fetchall()]

    def get_recent_crawl_logs(self, limit: int = 20) -> list[dict[str, Any]]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM crawl_log ORDER BY id DESC LIMIT ?", (limit,))
            return [dict(row) for row in cursor.fetchall()]

_sql_store_instance = None

def get_sql_store() -> SQLStore:
    global _sql_store_instance
    if _sql_store_instance is None:
        _sql_store_instance = SQLStore()
    return _sql_store_instance
