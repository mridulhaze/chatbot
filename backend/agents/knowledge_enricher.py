"""
Agent 2: Knowledge Enricher Agent
Ingests synthesized QA pairs, summaries, and key facts into ChromaDB vector store,
updates SQLite knowledge bases, and refreshes the in-memory fast retrieval index.
"""

import logging
from typing import Dict, Any, List, Optional
from langchain_core.documents import Document

from backend.crawler.db import get_crawler_db
from db.vector_store import get_vector_store
from backend.orchestrator.preloaded_responses import INSTANT_LOOKUP_MAP, ChatResponse, SourceCitation

logger = logging.getLogger("NU_KNOWLEDGE_ENRICHER")

class KnowledgeEnricherAgent:
    def __init__(self):
        self.vector_store = get_vector_store()

    def enrich_knowledge(self, analysis_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Takes structured analysis output and integrates it into the AI's multi-tier knowledge store.
        """
        url = analysis_result.get("url", "")
        title = analysis_result.get("title", "")
        section = analysis_result.get("section", "GENERAL")
        summary = analysis_result.get("summary_bn", "")
        qa_pairs = analysis_result.get("qa_pairs", [])
        key_facts = analysis_result.get("key_facts", [])

        docs_to_vectorize: List[Document] = []
        enriched_qa_count = 0

        # 1. Vectorize structured QA pairs
        for qa in qa_pairs:
            q_bn = qa.get("question_bn", "")
            a_bn = qa.get("answer_bn", "")
            q_en = qa.get("question_en", "")
            a_en = qa.get("answer_en", "")

            if q_bn and a_bn:
                qa_text = f"প্রশ্ন (FAQ): {q_bn}\nউত্তর: {a_bn}\n\nQuestion: {q_en}\nAnswer: {a_en}\n\nSource: {url}"
                docs_to_vectorize.append(Document(
                    page_content=qa_text,
                    metadata={
                        "source": url,
                        "title": title,
                        "section": section,
                        "type": "enriched_scraped_qa",
                        "language": "bilingual",
                        "question": q_bn
                    }
                ))
                enriched_qa_count += 1

        # 2. Vectorize summary & key facts card
        if summary or key_facts:
            summary_text = f"অফিসিয়াল সারসংক্ষেপ (Official Summary): {title}\n\n{summary}\n\nKey Facts:\n" + "\n".join([f"• {f}" for f in key_facts])
            docs_to_vectorize.append(Document(
                page_content=summary_text,
                metadata={
                    "source": url,
                    "title": title,
                    "section": section,
                    "type": "enriched_scraped_summary"
                }
            ))

        # 3. Ingest into ChromaDB
        if docs_to_vectorize:
            try:
                self.vector_store.split_and_add_documents(docs_to_vectorize)
                logger.info(f"Ingested {len(docs_to_vectorize)} enriched chunks for {url} into vector store.")
            except Exception as e:
                logger.warning(f"Vector store ingestion error for {url}: {e}")

        # 4. Insert into SQLite knowledge_enrichment_logs table
        log_id = self._save_enrichment_record(analysis_result, enriched_qa_count)

        # 5. Dynamically inject top synthesized QA into instant lookup cache
        for qa in qa_pairs[:2]:
            q_clean = qa.get("question_bn", "").lower().strip(" ?।!.,")
            if q_clean and len(q_clean) > 5 and q_clean not in INSTANT_LOOKUP_MAP:
                INSTANT_LOOKUP_MAP[q_clean] = ChatResponse(
                    reply=qa.get("answer_bn", ""),
                    citations=[SourceCitation(title=title, url=url, date="Enriched Knowledge")],
                    intent="ENRICHED_QA",
                    skill_used="content_classification",
                    suggested_chips=["📄 মূল নোটিশ", "🎫 সাপোর্ট টোকেন", "🏠 প্রধান মেনু"]
                )

        return {
            "log_id": log_id,
            "url": url,
            "title": title,
            "section": section,
            "qa_synthesized": enriched_qa_count,
            "chunks_vectorized": len(docs_to_vectorize)
        }

    def _save_enrichment_record(self, analysis_result: Dict[str, Any], qa_count: int) -> int:
        """Saves machine-readable record into SQLite knowledge_enrichment_logs table."""
        conn = get_crawler_db()
        try:
            with conn:
                conn.execute("""
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
                cursor = conn.execute("""
                    INSERT INTO knowledge_enrichment_logs (
                        url, title, section, summary_bn, qa_count, raw_analysis_json, agent_name
                    ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    analysis_result.get("url", ""),
                    analysis_result.get("title", ""),
                    analysis_result.get("section", "GENERAL"),
                    analysis_result.get("summary_bn", ""),
                    qa_count,
                    str(analysis_result),
                    analysis_result.get("analyzed_by", "KnowledgeEnricherAgent")
                ))
                return cursor.lastrowid
        finally:
            conn.close()

_knowledge_enricher_instance: Optional[KnowledgeEnricherAgent] = None

def get_knowledge_enricher() -> KnowledgeEnricherAgent:
    global _knowledge_enricher_instance
    if _knowledge_enricher_instance is None:
        _knowledge_enricher_instance = KnowledgeEnricherAgent()
    return _knowledge_enricher_instance
