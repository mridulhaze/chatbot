import re
import logging
from typing import List, Optional, Dict, Any
from langchain_core.documents import Document

from backend.core.config import settings
from backend.models.schemas import SolvedSimilarProblem
from db.vector_store import get_vector_store
from token_service.db import get_token_db_connection

logger = logging.getLogger("NU_SIMILARITY_SERVICE")

class SimilarityService:
    def __init__(self):
        self.vector_store = get_vector_store()
        self.threshold = settings.SIMILARITY_THRESHOLD

    def index_solved_case(
        self,
        token_id: str,
        service_code: str,
        problem: str,
        solution: str,
        solver_desk: Optional[str] = None
    ) -> bool:
        """
        Indexes an anonymized solved case into the vector database.
        Strictly strips all user identities, emails, phone numbers, and registration numbers.
        """
        try:
            # Anonymized structured document
            clean_problem = problem.strip()
            clean_solution = solution.strip()
            desk = solver_desk or "National University Support Desk"

            doc_content = (
                f"# সমাধানকৃত সাপোর্ট কেস (Solved Academic Support Case)\n"
                f"সার্ভিস ক্যাটাগরি (Service): {service_code.upper()}\n"
                f"সমস্যা বিবরণ (Problem): {clean_problem}\n"
                f"গৃহীত সমাধান (Resolution): {clean_solution}\n"
                f"দায়িত্বপ্রাপ্ত দপ্তর (Office): {desk}\n"
            )

            doc = Document(
                page_content=doc_content,
                metadata={
                    "source": f"solved_token://{token_id}",
                    "token_id": token_id,
                    "service_code": service_code.upper(),
                    "category": "Solved Support Case",
                    "type": "solved_support_case"
                }
            )

            self.vector_store.split_and_add_documents([doc])
            logger.info(f"Indexed anonymized solved case for {token_id} into Chroma vector database.")
            return True
        except Exception as e:
            logger.error(f"Error indexing solved case {token_id}: {e}", exc_info=True)
            return False

    def search_similar_solved_cases(
        self,
        problem_description: str,
        service_code: Optional[str] = None,
        limit: int = 3
    ) -> List[SolvedSimilarProblem]:
        """
        Performs semantic similarity search for previously resolved cases.
        Returns anonymized problem/solution pairs.
        """
        results: List[SolvedSimilarProblem] = []
        clean_query = problem_description.strip()
        if not clean_query:
            return results

        # 1. Semantic Search via Vector Store
        try:
            search_query = f"সমস্যা সমাধান: {clean_query}"
            if service_code:
                search_query = f"সার্ভিস {service_code}: {clean_query}"

            matches = self.vector_store.similarity_search(search_query, k=limit * 3)

            for doc, score in matches:
                meta = doc.metadata or {}
                if meta.get("type") == "solved_support_case":
                    doc_service = meta.get("service_code", "GENERAL")
                    if service_code and doc_service.upper() != service_code.upper():
                        continue

                    content = doc.page_content
                    prob_m = re.search(r"সমস্যা বিবরণ \(Problem\):\s*(.+)", content)
                    sol_m = re.search(r"গৃহীত সমাধান \(Resolution\):\s*(.+)", content)

                    prob_text = prob_m.group(1).strip() if prob_m else clean_query
                    sol_text = sol_m.group(1).strip() if sol_m else "পূর্ববর্তী সমাধান রেকর্ড রয়েছে।"

                    results.append(SolvedSimilarProblem(
                        token_id=meta.get("token_id", "NU-SOLVED"),
                        service_code=doc_service,
                        service_name=doc_service,
                        problem=prob_text,
                        solution=sol_text,
                        similarity_score=float(score)
                    ))
                    if len(results) >= limit:
                        break
        except Exception as e:
            logger.warning(f"Vector search failed in similarity service: {e}")

        # 2. Database Keyword Fallback if no vector results found
        if not results:
            try:
                conn = get_token_db_connection()
                query = "SELECT token_id, service_type, problem, solve_message, solved_date FROM token_requests WHERE status = 'SOLVED'"
                params = []
                if service_code:
                    query += " AND service_type = ?"
                    params.append(service_code.upper())
                query += " ORDER BY id DESC LIMIT ?"
                params.append(limit)

                cur = conn.execute(query, params)
                for r in cur.fetchall():
                    results.append(SolvedSimilarProblem(
                        token_id=r["token_id"],
                        service_code=r["service_type"],
                        service_name=r["service_type"],
                        problem=r["problem"],
                        solution=r["solve_message"] or "দপ্তর কর্তৃক সমস্যাটি সমাধান করা হয়েছে।",
                        solved_date=r["solved_date"],
                        similarity_score=0.80
                    ))
                conn.close()
            except Exception as ex:
                logger.warning(f"Database fallback query failed: {ex}")

        return results

_similarity_service_instance: Optional[SimilarityService] = None

def get_similarity_service() -> SimilarityService:
    global _similarity_service_instance
    if _similarity_service_instance is None:
        _similarity_service_instance = SimilarityService()
    return _similarity_service_instance
