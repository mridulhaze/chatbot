import sqlite3
from pathlib import Path

class CrawlDB:
    def __init__(self, path):
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(path, check_same_thread=False)
        self.conn.execute("PRAGMA journal_mode=WAL")
        self.conn.execute("PRAGMA synchronous=NORMAL")
        self.init()

    def init(self):
        self.conn.executescript("""
        CREATE TABLE IF NOT EXISTS urls (
            url TEXT PRIMARY KEY,
            status TEXT NOT NULL DEFAULT 'queued',
            depth INTEGER NOT NULL DEFAULT 0,
            parent_url TEXT,
            discovered_from TEXT,
            http_status INTEGER,
            content_type TEXT,
            title TEXT,
            error TEXT,
            crawled_at TEXT
        );
        CREATE TABLE IF NOT EXISTS documents (
            url TEXT PRIMARY KEY,
            parent_url TEXT,
            content_type TEXT,
            local_path TEXT,
            sha256 TEXT,
            extracted INTEGER DEFAULT 0,
            crawled_at TEXT
        );
        CREATE TABLE IF NOT EXISTS links (
            source_url TEXT,
            target_url TEXT,
            label TEXT,
            relation TEXT,
            PRIMARY KEY(source_url, target_url, label)
        );
        CREATE INDEX IF NOT EXISTS idx_urls_status ON urls(status);
        """)
        self.conn.commit()

    def add_url(self, url, depth=0, parent_url=None, discovered_from=None):
        self.conn.execute(
            "INSERT OR IGNORE INTO urls(url,status,depth,parent_url,discovered_from) VALUES(?,?,?,?,?)",
            (url, "queued", depth, parent_url, discovered_from)
        )
        self.conn.commit()

    def add_urls(self, items):
        self.conn.executemany(
            "INSERT OR IGNORE INTO urls(url,status,depth,parent_url,discovered_from) VALUES(?,?,?,?,?)",
            [(a, "queued", b, c, d) for a, b, c, d in items]
        )
        self.conn.commit()

    def get_next(self):
        return self.conn.execute(
            "SELECT url,depth,parent_url FROM urls WHERE status='queued' ORDER BY depth,rowid LIMIT 1"
        ).fetchone()

    def mark_started(self, url):
        self.conn.execute("UPDATE urls SET status='processing' WHERE url=?", (url,))
        self.conn.commit()

    def mark_done(self, url, http_status=None, content_type=None, title=None, crawled_at=None):
        self.conn.execute(
            "UPDATE urls SET status='done',http_status=?,content_type=?,title=?,crawled_at=?,error=NULL WHERE url=?",
            (http_status,content_type,title,crawled_at,url)
        )
        self.conn.commit()

    def mark_error(self, url, error, http_status=None, crawled_at=None):
        self.conn.execute(
            "UPDATE urls SET status='error',http_status=?,error=?,crawled_at=? WHERE url=?",
            (http_status,error[:2000],crawled_at,url)
        )
        self.conn.commit()

    def add_link(self, source, target, label, relation):
        self.conn.execute(
            "INSERT OR IGNORE INTO links(source_url,target_url,label,relation) VALUES(?,?,?,?)",
            (source,target,label[:500],relation)
        )
        self.conn.commit()

    def add_document(self, record):
        self.conn.execute(
            """INSERT OR REPLACE INTO documents
            (url,parent_url,content_type,local_path,sha256,extracted,crawled_at)
            VALUES(?,?,?,?,?,?,?)""",
            (record["url"],record.get("parent_url"),record.get("content_type"),
             record.get("local_path"),record.get("sha256"),
             1 if record.get("extracted") else 0,record.get("crawled_at"))
        )
        self.conn.commit()

    def stats(self):
        return dict(self.conn.execute("SELECT status,COUNT(*) FROM urls GROUP BY status").fetchall())

    def close(self):
        self.conn.close()
