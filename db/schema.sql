-- Database Schema for National University AI Knowledge Base & Self-Enrichment Store

CREATE TABLE IF NOT EXISTS notices (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    url TEXT UNIQUE NOT NULL,
    pdf_url TEXT,
    category TEXT DEFAULT 'General',
    published_date TEXT,
    content_hash TEXT,
    raw_text TEXT,
    scraped_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS admission_info (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    program TEXT NOT NULL,
    level TEXT,
    eligibility TEXT,
    deadline TEXT,
    notes TEXT,
    source_url TEXT,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS faq_entries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    question TEXT NOT NULL,
    answer TEXT NOT NULL,
    source_url TEXT,
    language TEXT DEFAULT 'bn',
    category TEXT DEFAULT 'General',
    confidence REAL DEFAULT 1.0,
    verified_by_admin INTEGER DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS gap_queue (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_query TEXT NOT NULL,
    language TEXT DEFAULT 'bn',
    session_id TEXT,
    reason TEXT,
    status TEXT DEFAULT 'pending', -- pending, researching, candidate_ready, resolved, rejected
    candidate_answer TEXT,
    confidence REAL DEFAULT 0.0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    resolved_at DATETIME
);

CREATE TABLE IF NOT EXISTS crawl_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source TEXT NOT NULL,
    status TEXT NOT NULL, -- success, partial, failed
    started_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    finished_at DATETIME,
    pages_scraped INTEGER DEFAULT 0,
    new_items INTEGER DEFAULT 0,
    errors TEXT
);

CREATE TABLE IF NOT EXISTS officers_directory (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    department_slug TEXT,
    department_name TEXT,
    department_url TEXT,
    name TEXT NOT NULL,
    designation_bn TEXT,
    designation_en TEXT,
    phone TEXT,
    email TEXT,
    raw_details TEXT,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_officer_dept ON officers_directory (department_slug);
CREATE INDEX IF NOT EXISTS idx_officer_name ON officers_directory (name);
CREATE INDEX IF NOT EXISTS idx_officer_desig ON officers_directory (designation_bn, designation_en);


CREATE INDEX IF NOT EXISTS idx_notices_date ON notices(published_date);
CREATE INDEX IF NOT EXISTS idx_faq_question ON faq_entries(question);
CREATE INDEX IF NOT EXISTS idx_gap_status ON gap_queue(status);
