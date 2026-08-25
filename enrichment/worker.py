import os
import time
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional
from dotenv import load_dotenv
from google import genai
from langchain_core.documents import Document

from db.sql_store import get_sql_store
from db.vector_store import get_vector_store

load_dotenv()
logger = logging.getLogger("NU_ENRICHMENT_WORKER")

class GapEnrichmentWorker:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = (api_key or os.getenv("GEMINI_API_KEY", "")).strip()
        self.client = genai.Client(api_key=self.api_key) if self.api_key else None
        self.sql_store = get_sql_store()
        self.vector_store = get_vector_store()
        self.model_candidates = [
            "gemini-3.5-flash",
            "gemini-flash-latest",
            "gemini-2.5-flash-lite",
            "gemini-3.1-flash-lite-preview"
        ]

    def _generate_candidate_answer(self, query: str, language: str = "bn") -> Optional[Dict[str, Any]]:
        if not self.client:
            logger.warning("Gemini Client not initialized. Skipping gap generation.")
            return None

        prompt = f"""You are an expert academic counselor and information specialist for the National University of Bangladesh (জাতীয় বিশ্ববিদ্যালয়, nu.ac.bd).
A student asked the following question which was not found in our current knowledge base:
"{query}"

Tasks:
1. Provide a clear, fact-grounded answer based on official National University Bangladesh regulations, syllabus, admission rules, examination guidelines, and portal procedures.
2. Include the official portal links:
   - Notices: https://www.nu.ac.bd/
   - Admission: http://app1.nu.edu.bd/
   - Results & Grading: https://results.nu.ac.bd/
   - Form Fill-up & EMS: http://ems.nu.ac.bd/
3. Reply in the same language as the user query ({'Bengali/বাংলা' if language == 'bn' else 'English'}).
4. Be strictly truthful. If a specific date/schedule varies by year, explain how and where the student can verify the official circular. Do not fabricate arbitrary dates.

Output format (Markdown):
"""
        for model in self.model_candidates:
            try:
                response = self.client.models.generate_content(
                    model=model,
                    contents=prompt
                )
                if response and response.text:
                    return {
                        "answer": response.text.strip(),
                        "confidence": 0.90,
                        "source_url": "https://www.nu.ac.bd/"
                    }
            except Exception as e:
                logger.warning(f"Model {model} failed during enrichment: {e}")
                time.sleep(1)
        return None

    def process_pending_gaps(self, auto_approve_threshold: float = 0.95) -> Dict[str, Any]:
        """
        Pulls all 'pending' gaps from the database, synthesizes candidate answers,
        and saves them as 'candidate_ready' (or auto-approves if high confidence).
        """
        pending_gaps = self.sql_store.get_gap_queue(status="pending", limit=20)
        logger.info(f"Found {len(pending_gaps)} pending gaps to enrich.")
        
        enriched_count = 0
        auto_approved_count = 0

        for gap in pending_gaps:
            gap_id = gap["id"]
            user_query = gap["user_query"]
            lang = gap.get("language") or "bn"

            self.sql_store.update_gap_status(gap_id, status="researching")
            result = self._generate_candidate_answer(user_query, language=lang)
            
            if result:
                candidate_answer = result["answer"]
                confidence = result.get("confidence", 0.90)

                # Store draft in FAQ table (unverified)
                faq_id = self.sql_store.insert_faq_entry(
                    question=user_query,
                    answer=candidate_answer,
                    source_url=result.get("source_url", "https://www.nu.ac.bd/"),
                    language=lang,
                    category="Self-Enriched",
                    confidence=confidence,
                    verified_by_admin=0
                )

                if confidence >= auto_approve_threshold:
                    self.sql_store.approve_gap_entry(gap_id, custom_answer=candidate_answer)
                    # Add to vector store directly
                    doc = Document(
                        page_content=f"Q: {user_query}\nA: {candidate_answer}",
                        metadata={"source": "self_enrichment", "type": "faq_verified"}
                    )
                    self.vector_store.split_and_add_documents([doc])
                    auto_approved_count += 1
                else:
                    self.sql_store.update_gap_status(
                        gap_id=gap_id,
                        status="candidate_ready",
                        candidate_answer=candidate_answer,
                        confidence=confidence
                    )

                enriched_count += 1
            else:
                self.sql_store.update_gap_status(gap_id, status="pending")

            time.sleep(1.0)

        return {
            "processed": len(pending_gaps),
            "enriched": enriched_count,
            "auto_approved": auto_approved_count
        }

    def approve_gap(self, gap_id: int, custom_answer: Optional[str] = None) -> bool:
        """Admin manual approval of a gap entry."""
        faq_id = self.sql_store.approve_gap_entry(gap_id, custom_answer=custom_answer)
        if faq_id:
            # Also feed to vector DB
            with self.sql_store._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM faq_entries WHERE id = ?", (faq_id,))
                faq = cursor.fetchone()
                if faq:
                    doc = Document(
                        page_content=f"Q: {faq['question']}\nA: {faq['answer']}",
                        metadata={"source": "admin_approved_faq", "type": "faq_verified"}
                    )
                    self.vector_store.split_and_add_documents([doc])
            return True
        return False

    def reject_gap(self, gap_id: int) -> bool:
        self.sql_store.update_gap_status(gap_id, status="rejected")
        return True

_enrichment_worker_instance = None

def get_enrichment_worker() -> GapEnrichmentWorker:
    global _enrichment_worker_instance
    if _enrichment_worker_instance is None:
        _enrichment_worker_instance = GapEnrichmentWorker()
    return _enrichment_worker_instance
