"""
Agent 3: Knowledge Provenance & Changelog Agent
Records all knowledge updates in standardized, machine-readable formats (JSONL, JSON Manifest, and Markdown Changelog)
so other AI agents (Claude, Codex, Antigravity subagents, or external systems) can inspect, verify provenance, and proceed.
"""

import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, List, Optional

from backend.core.config import settings
from backend.crawler.db import get_crawler_db

logger = logging.getLogger("NU_KNOWLEDGE_PROVENANCE")

JSONL_UPDATES_PATH = settings.DATA_DIR / "knowledge_updates.jsonl"
CHANGELOG_MD_PATH = settings.DATA_DIR / "KNOWLEDGE_CHANGELOG.md"
MANIFEST_JSON_PATH = settings.DATA_DIR / "knowledge_manifest.json"

class KnowledgeProvenanceAgent:
    def __init__(self):
        settings.DATA_DIR.mkdir(parents=True, exist_ok=True)

    def record_update(self, update_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Saves update to JSONL, updates the Markdown changelog, and generates the latest knowledge manifest.
        """
        now_iso = datetime.now(timezone.utc).isoformat()
        record_id = f"KNOW-UPD-{int(datetime.now().timestamp() * 1000)}"

        entry = {
            "update_id": record_id,
            "timestamp_iso": now_iso,
            "source_url": update_data.get("url", ""),
            "title": update_data.get("title", ""),
            "section": update_data.get("section", "GENERAL"),
            "summary_bn": update_data.get("summary_bn", ""),
            "qa_count": len(update_data.get("qa_pairs", [])),
            "qa_pairs": update_data.get("qa_pairs", []),
            "key_facts": update_data.get("key_facts", []),
            "analyzed_by": update_data.get("analyzed_by", "ScrapedDataAnalyzerAgent"),
            "status": "active"
        }

        # 1. Append to JSONL Stream
        try:
            with open(JSONL_UPDATES_PATH, "a", encoding="utf-8") as f:
                f.write(json.dumps(entry, ensure_ascii=False) + "\n")
        except Exception as e:
            logger.error(f"Error appending to JSONL log: {e}")

        # 2. Update Markdown Changelog & Manifest
        self.refresh_manifest_and_changelog()

        return entry

    def refresh_manifest_and_changelog(self) -> Dict[str, Any]:
        """
        Recompiles the Knowledge Manifest and Markdown Changelog from SQLite and JSONL logs.
        """
        conn = get_crawler_db()
        cursor = conn.cursor()
        total_enriched_pages = 0
        total_pages = 0
        total_logs = 0
        total_qa = 0
        recent_logs = []
        try:
            # Ensure tables exist
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS knowledge_enrichment_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    url TEXT NOT NULL,
                    title TEXT,
                    section TEXT,
                    summary_bn TEXT,
                    qa_count INTEGER DEFAULT 0,
                    raw_analysis_json TEXT,
                    agent_name TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.commit()

            # Check pages table safely
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='pages'")
            if cursor.fetchone():
                cursor.execute("PRAGMA table_info(pages)")
                columns = [c[1] for c in cursor.fetchall()]
                if "is_enriched" in columns:
                    cursor.execute("SELECT COUNT(*) FROM pages WHERE is_enriched = 1")
                    total_enriched_pages = cursor.fetchone()[0]
                cursor.execute("SELECT COUNT(*) FROM pages")
                total_pages = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM knowledge_enrichment_logs")
            total_logs = cursor.fetchone()[0]

            cursor.execute("SELECT SUM(qa_count) FROM knowledge_enrichment_logs")
            total_qa = cursor.fetchone()[0] or 0

            cursor.execute("""
                SELECT id, url, title, section, summary_bn, qa_count, agent_name, created_at
                FROM knowledge_enrichment_logs
                ORDER BY id DESC
                LIMIT 25
            """)
            recent_logs = [dict(r) for r in cursor.fetchall()]
        except Exception as e:
            logger.warning(f"Error querying knowledge enrichment telemetry: {e}")
        finally:
            conn.close()

        now_iso = datetime.now(timezone.utc).isoformat()
        manifest = {
            "$schema": "https://json-schema.org/draft/2020-12/schema",
            "manifest_version": "2.0.0",
            "standard": "Antigravity/MCP AI Knowledge Exchange Standard",
            "last_updated_iso": now_iso,
            "knowledge_base_name": "National University Bangladesh Official Knowledge Base",
            "root_domain": "https://www.nu.ac.bd/",
            "statistics": {
                "total_crawled_pages": total_pages,
                "total_enriched_pages": total_enriched_pages,
                "total_enrichment_cycles": total_logs,
                "total_synthesized_qa": total_qa
            },
            "inter_agent_instructions": (
                "Any secondary AI agent (Claude, Codex, Antigravity, or external RAG) should load "
                "knowledge_updates.jsonl or query the enrichment_mcp server tool 'get_recent_knowledge_updates' "
                "to synchronize new academic circulars, exam routines, and admission notices."
            ),
            "recent_enrichments": recent_logs
        }

        # Write Manifest JSON
        try:
            with open(MANIFEST_JSON_PATH, "w", encoding="utf-8") as f:
                json.dump(manifest, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"Error saving knowledge_manifest.json: {e}")

        # Write Markdown Changelog
        try:
            md_lines = [
                "# 📜 National University AI Knowledge Changelog",
                f"> **Last Synchronized (UTC):** `{now_iso}`  ",
                f"> **Total Enriched Pages:** `{total_enriched_pages}` | **Total QA Pairs:** `{total_qa}`  ",
                "\n---\n",
                "## 🕒 Recent Autonomous Knowledge Updates\n"
            ]

            for log in recent_logs:
                md_lines.append(f"### 📌 #{log['id']} - {log['title'] or 'Academic Update'}")
                md_lines.append(f"- **Section:** `{log['section']}` | **Date:** `{log['created_at']}`")
                md_lines.append(f"- **Source:** [{log['url']}]({log['url']})")
                md_lines.append(f"- **Summary:** {log['summary_bn'] or 'No summary recorded.'}")
                md_lines.append(f"- **Synthesized QA:** `{log['qa_count']}` pairs | **Agent:** `{log['agent_name']}`\n")

            with open(CHANGELOG_MD_PATH, "w", encoding="utf-8") as f:
                f.write("\n".join(md_lines))
        except Exception as e:
            logger.error(f"Error saving KNOWLEDGE_CHANGELOG.md: {e}")

        return manifest

    def get_manifest(self) -> Dict[str, Any]:
        """Returns the current knowledge manifest."""
        if MANIFEST_JSON_PATH.exists():
            try:
                with open(MANIFEST_JSON_PATH, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error reading manifest: {e}")
        return self.refresh_manifest_and_changelog()

    def get_recent_updates_stream(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Reads recent entries from JSONL log."""
        if not JSONL_UPDATES_PATH.exists():
            return []
        
        records = []
        try:
            with open(JSONL_UPDATES_PATH, "r", encoding="utf-8") as f:
                for line in f:
                    line_str = line.strip()
                    if line_str:
                        records.append(json.loads(line_str))
            return records[-limit:][::-1]
        except Exception as e:
            logger.error(f"Error reading JSONL updates: {e}")
            return []

_knowledge_provenance_instance: Optional[KnowledgeProvenanceAgent] = None

def get_knowledge_provenance() -> KnowledgeProvenanceAgent:
    global _knowledge_provenance_instance
    if _knowledge_provenance_instance is None:
        _knowledge_provenance_instance = KnowledgeProvenanceAgent()
    return _knowledge_provenance_instance
