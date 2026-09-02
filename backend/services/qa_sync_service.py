import sys
import json
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from langchain_core.documents import Document
from db.sql_store import SQLStore, get_sql_store
from db.vector_store import get_vector_store

logger = logging.getLogger("NU_QA_SYNC")

DATA_FILE = Path(__file__).resolve().parent.parent.parent / "data" / "nu_qa_dataset.json"

class QASyncService:
    def __init__(self):
        self.sql_store = get_sql_store()
        self._vector_store = None

    @property
    def vector_store(self):
        if self._vector_store is None:
            self._vector_store = get_vector_store()
        return self._vector_store

    def sync_all(self, sync_vector_db: bool = True) -> Dict[str, Any]:
        """
        Synchronizes all 100 Q&A items and variations to SQL and Vector DB.
        """
        if not DATA_FILE.exists():
            raise FileNotFoundError(f"Q&A Dataset not found at: {DATA_FILE}")

        with open(DATA_FILE, "r", encoding="utf-8") as f:
            qa_items: List[Dict[str, Any]] = json.load(f)

        faq_records: List[Dict[str, Any]] = []
        documents: List[Document] = []

        for item in qa_items:
            q_id = item.get("id")
            category = item.get("category", "General")
            intent = item.get("intent", "GENERAL_SUPPORT")
            q_bn = item.get("question_bn", "")
            q_banglish = item.get("question_banglish", "")
            q_en = item.get("question_en", "")
            ans_bn = item.get("answer_bn", item.get("answer", ""))
            ans_en = item.get("answer_en", "")
            source_url = item.get("source_url", "https://www.nu.ac.bd/")
            variations = item.get("variations", [])
            keywords = item.get("keywords", [])

            # 1. Primary Bengali QA
            faq_records.append({
                "question": q_bn,
                "answer": ans_bn,
                "source_url": source_url,
                "language": "bn",
                "category": category,
                "confidence": item.get("confidence", 1.0),
                "verified_by_admin": 1
            })

            # 2. English version if available
            if q_en and ans_en:
                faq_records.append({
                    "question": q_en,
                    "answer": ans_en,
                    "source_url": source_url,
                    "language": "en",
                    "category": category,
                    "confidence": item.get("confidence", 1.0),
                    "verified_by_admin": 1
                })

            # 3. Variations (Banglish, typo, informal)
            for var in variations:
                faq_records.append({
                    "question": var,
                    "answer": ans_bn,
                    "source_url": source_url,
                    "language": "banglish" if var.isascii() else "bn",
                    "category": category,
                    "confidence": item.get("confidence", 1.0),
                    "verified_by_admin": 1
                })

            # 4. Construct semantic vector document
            doc_content = (
                f"# জাতীয় বিশ্ববিদ্যালয় প্রশ্নোত্তর (Q&A ID: {q_id})\n"
                f"ক্যাটাগরি (Category): {category}\n"
                f"ইনটেন্ট (Intent): {intent}\n"
                f"প্রশ্ন (বাংলা): {q_bn}\n"
                f"Question (Banglish): {q_banglish}\n"
                f"Question (English): {q_en}\n"
                f"প্রশ্ন রূপভেদ (Variations): {', '.join(variations)}\n"
                f"উত্তর (Bangla Answer):\n{ans_bn}\n\n"
                f"Answer (English):\n{ans_en}\n"
                f"কীওয়ার্ডস (Keywords): {', '.join(keywords)}\n"
                f"অফিসিয়াল লিংক: {source_url}\n"
            )

            doc = Document(
                page_content=doc_content,
                metadata={
                    "source": f"faq://{q_id}",
                    "id": q_id,
                    "category": category,
                    "intent": intent,
                    "source_url": source_url,
                    "source_type": item.get("source_type", "official_portal"),
                    "requires_live_check": item.get("requires_live_check", False),
                    "requires_student_auth": item.get("requires_student_auth", False),
                    "confidence": item.get("confidence", 1.0)
                }
            )
            documents.append(doc)

        sql_inserted = self.sql_store.batch_upsert_faqs(faq_records)

        # 5. Push to Vector DB if enabled
        indexed_chunks = 0
        if sync_vector_db and documents:
            try:
                indexed_chunks = self.vector_store.split_and_add_documents(documents)
            except Exception as e:
                logger.warning(f"Vector DB indexing deferred or skipped: {e}")

        logger.info(f"Synchronized {len(qa_items)} Q&A items ({sql_inserted} SQLite records, {len(documents)} vector docs).")
        return {
            "status": "SUCCESS",
            "total_qa_items": len(qa_items),
            "sqlite_records_synced": sql_inserted,
            "vector_documents_prepared": len(documents),
            "vector_chunks_indexed": indexed_chunks
        }

_sync_service_instance: Optional[QASyncService] = None

def get_qa_sync_service() -> QASyncService:
    global _sync_service_instance
    if _sync_service_instance is None:
        _sync_service_instance = QASyncService()
    return _sync_service_instance

def sync_qa_database(sync_vector: bool = True) -> Dict[str, Any]:
    service = get_qa_sync_service()
    return service.sync_all(sync_vector_db=sync_vector)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    result = sync_qa_database()
    print(json.dumps(result, indent=2, ensure_ascii=False))
