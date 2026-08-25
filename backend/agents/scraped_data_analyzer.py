"""
Agent 1: Scraped Data & Content Analyzer Agent
Analyzes newly crawled pages and documents from National University,
extracts academic entities, rules, deadlines, and synthesizes high-quality QA pairs.
"""

import os
import re
import json
import logging
from typing import Dict, Any, List, Optional
from google import genai
from google.genai import types

from backend.core.config import settings
from backend.crawler.db import get_crawler_db

logger = logging.getLogger("NU_SCRAPED_DATA_ANALYZER")

class ScrapedDataAnalyzerAgent:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = (api_key or settings.GEMINI_API_KEY).strip()
        self.client = genai.Client(api_key=self.api_key) if self.api_key else None
        self.models = [settings.PRIMARY_MODEL] + settings.FALLBACK_MODELS

    def analyze_page(self, page_record: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyzes a single scraped page, extracts structured insights and synthesizes QA pairs.
        """
        url = page_record.get("url", "")
        title = page_record.get("title", "")
        content = page_record.get("content_text", "")
        section = page_record.get("section", "GENERAL")
        published_date = page_record.get("published_date") or ""

        # Fallback quick synthesis if content is short or LLM offline
        if not content or len(content.strip()) < 40:
            return {
                "url": url,
                "title": title,
                "section": section,
                "summary_bn": f"{title} সংক্রান্ত অফিসিয়াল বিজ্ঞপ্তি।",
                "entities": {"dates": [], "links": [url]},
                "qa_pairs": [
                    {
                        "question_bn": f"{title} সম্পর্কে বিস্তারিত কীভাবে জানা যাবে?",
                        "answer_bn": f"জাতীয় বিশ্ববিদ্যালয়ের অফিসিয়াল ওয়েবসাইটে এই সংক্রান্ত তথ্য পাওয়া যাবে: {url}",
                        "question_en": f"How to get details about {title}?",
                        "answer_en": f"Official details are published at National University portal: {url}"
                    }
                ],
                "confidence": 0.80,
                "analyzed_by": "RuleBasedAnalyzer"
            }

        # Use Gemini Fast Flash LLM to extract deep insights
        if self.client:
            prompt = f"""You are an expert Academic Knowledge Analyst Agent for National University Bangladesh (nu.ac.bd).
Analyze the following scraped university content:

=== SOURCE DETAILS ===
URL: {url}
Title: {title}
Section: {section}
Published Date: {published_date}
Content:
{content[:2500]}
=== END SOURCE ===

TASKS:
1. Generate a clear, concise summary in Bengali (summary_bn, 2-3 sentences).
2. Extract key entities: dates, deadlines, fees, departments, related URLs.
3. Synthesize 2-4 realistic, highly useful Student Question & Answer pairs based STRICTLY on the content (in both Bengali and English).

Respond ONLY in valid JSON format matching this schema:
{{
  "summary_bn": "...",
  "key_facts": ["...", "..."],
  "entities": {{
    "dates": ["..."],
    "fees": ["..."],
    "links": ["{url}"]
  }},
  "qa_pairs": [
    {{
      "question_bn": "...",
      "answer_bn": "...",
      "question_en": "...",
      "answer_en": "..."
    }}
  ]
}}
"""
            config = types.GenerateContentConfig(
                max_output_tokens=800,
                temperature=0.2,
                response_mime_type="application/json"
            )

            for model_name in self.models:
                try:
                    res = self.client.models.generate_content(
                        model=model_name,
                        contents=prompt,
                        config=config
                    )
                    if res and res.text:
                        parsed = json.loads(res.text.strip())
                        return {
                            "url": url,
                            "title": title,
                            "section": section,
                            "summary_bn": parsed.get("summary_bn", f"{title} সংক্রান্ত বিস্তারিত তথ্য।"),
                            "key_facts": parsed.get("key_facts", []),
                            "entities": parsed.get("entities", {"links": [url]}),
                            "qa_pairs": parsed.get("qa_pairs", []),
                            "confidence": 0.95,
                            "analyzed_by": f"GeminiAnalyzer ({model_name})"
                        }
                except Exception as e:
                    logger.warning(f"Model {model_name} failed in ScrapedDataAnalyzerAgent: {e}")

        # Algorithmic Rule-based Fallback
        return self._algorithmic_analysis(page_record)

    def _algorithmic_analysis(self, page_record: Dict[str, Any]) -> Dict[str, Any]:
        """
        Deterministic, offline extraction when external API is rate-limited.
        """
        url = page_record.get("url", "")
        title = page_record.get("title", "")
        content = page_record.get("content_text", "")
        section = page_record.get("section", "GENERAL")

        # Extract dates using regex
        date_matches = re.findall(r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b|\b\d{1,2}\s+(?:জানুয়ারি|ফেব্রুয়ারি|মার্চ|এপ্রিল|মে|জুন|জুলাই|আগস্ট|সেপ্টেম্বর|অক্টোবর|নভেম্বর|ডিসেম্বর|January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{4}\b', content, re.IGNORECASE)

        sentences = [s.strip() for s in re.split(r'[।\n.]+', content) if len(s.strip()) > 15]
        summary = " । ".join(sentences[:2]) + "।" if sentences else f"{title} সংক্রান্ত নোটিশ।"

        qa_pairs = [
            {
                "question_bn": f"{title} এর মূল বিষয়বস্তু কী?",
                "answer_bn": f"{summary} বিস্তারিত দেখতে ক্লিক করুন: {url}",
                "question_en": f"What is the summary of {title}?",
                "answer_en": f"{summary} For full official details, visit: {url}"
            }
        ]

        return {
            "url": url,
            "title": title,
            "section": section,
            "summary_bn": summary,
            "key_facts": sentences[:3],
            "entities": {
                "dates": list(set(date_matches)),
                "links": [url]
            },
            "qa_pairs": qa_pairs,
            "confidence": 0.85,
            "analyzed_by": "RuleBasedAnalyzer (Offline)"
        }

    def get_unanalyzed_pages(self, limit: int = 15) -> List[Dict[str, Any]]:
        """
        Fetches pages from SQLite that have not yet been processed by the 24/7 analysis agent.
        """
        conn = get_crawler_db()
        cursor = conn.cursor()
        try:
            # Check if enrichment tracking column exists, else add it
            cursor.execute("PRAGMA table_info(pages)")
            columns = [c[1] for c in cursor.fetchall()]
            if "is_enriched" not in columns:
                cursor.execute("ALTER TABLE pages ADD COLUMN is_enriched INTEGER DEFAULT 0")
                cursor.execute("ALTER TABLE pages ADD COLUMN enriched_at TIMESTAMP")
                conn.commit()

            cursor.execute("""
                SELECT id, url, title, section, COALESCE(clean_text, content, '') as content_text, published_date, content_hash
                FROM pages
                WHERE is_enriched = 0 OR is_enriched IS NULL
                ORDER BY id DESC
                LIMIT ?
            """, (limit,))
            rows = cursor.fetchall()
            return [dict(r) for r in rows]
        finally:
            conn.close()

    def mark_page_enriched(self, page_id: int):
        """Marks a page as analyzed and enriched."""
        conn = get_crawler_db()
        try:
            with conn:
                conn.execute("""
                    UPDATE pages
                    SET is_enriched = 1, enriched_at = datetime('now')
                    WHERE id = ?
                """, (page_id,))
        finally:
            conn.close()

_scraped_data_analyzer_instance: Optional[ScrapedDataAnalyzerAgent] = None

def get_scraped_data_analyzer() -> ScrapedDataAnalyzerAgent:
    global _scraped_data_analyzer_instance
    if _scraped_data_analyzer_instance is None:
        _scraped_data_analyzer_instance = ScrapedDataAnalyzerAgent()
    return _scraped_data_analyzer_instance
