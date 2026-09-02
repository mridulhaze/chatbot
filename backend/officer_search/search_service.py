"""
National University Bangladesh AI Assistant — Officer Search Service
Main facade orchestrating normalization, entity extraction, database matching, ranking, and response formatting.
"""

import time
import logging
from typing import Dict, Any, List, Optional, Tuple

from .entity_extractor import extract_directory_entities, OfficerQueryEntities
from .matcher import OfficerMatcher
from .formatter import format_officer_response
from backend.models import SourceCitation, ChatResponse

logger = logging.getLogger("NU_OFFICER_SEARCH")

# In-memory query cache with TTL (5 minutes)
_QUERY_CACHE: Dict[str, Tuple[float, Any]] = {}
CACHE_TTL_SECONDS = 300


class OfficerSearchService:
    def __init__(self):
        self.matcher = OfficerMatcher()

    def is_directory_query(self, query: str, history: Optional[List[Any]] = None) -> bool:
        """
        Determines whether a user query should be handled by the structured officer search engine.
        Returns False if the query is general knowledge or unrelated to staff/offices.
        """
        if not query or not query.strip():
            return False

        q_lower = query.lower()
        # Explicitly guard against result, notice, admission, year, token, and service queries from being hijacked as names
        result_terms = [
            "result", "results", "রেজাল্ট", "ফলাফল", "cgpa", "gpa", "marksheet", "পুনঃনিরীক্ষণ",
            "4th year", "1st year", "2nd year", "3rd year", "final year", "১ম বর্ষ", "২য় বর্ষ", "৩য় বর্ষ", "৪র্থ বর্ষ",
            "exam", "examination", "পরীক্ষা", "routine", "রুটিন",
            "token", "tokens", "ticket", "tickets", "টোকেন", "টিকিট", "token service", "support token", "check token",
            "token status", "টোকেন স্ট্যাটাস", "টোকেন চেক", "টোকেন সার্ভিস", "টোকেন সেবা", "টোকেন নম্বর"
        ]
        if any(w in q_lower for w in result_terms):
            return False

        entities = extract_directory_entities(query, history)
        if entities.is_general_knowledge:
            return False

        if (
            entities.is_all_departments_query
            or entities.is_all_query
            or entities.department_slug
            or entities.designation
            or entities.phone
            or entities.email
        ):
            return True

        # If name is present, verify it matches known directory indicator or actual person query
        if entities.name and len(entities.name) >= 2:
            # If query has directory keywords (officer, employee, contact, info, etc.) or is a pure name
            dir_indicators = ["কর্মকর্তা", "কর্মচারী", "যোগাযোগ", "ফোন", "ইমেইল", "officer", "employee", "staff", "contact", "phone", "email", "number", "নম্বর"]
            if any(ind in q_lower for ind in dir_indicators):
                return True
            # Check if name is not an academic term like "honours", "admission", "routine", "token"
            non_name_terms = [
                "honours", "degree", "masters", "admission", "routine", "notice", "syllabus",
                "token", "tokens", "ticket", "service", "status", "check",
                "ভর্তি", "রুটিন", "নোটিশ", "সিলেবাস", "টোকেন", "টিকিট", "সার্ভিস", "স্ট্যাটাস", "চেক", "সেবা",
                "1st", "2nd", "3rd", "4th", "year", "বর্ষ"
            ]
            if not any(term in q_lower for term in non_name_terms):
                return True

        return False

    def search_and_format(
        self,
        query: str,
        history: Optional[List[Any]] = None,
        page: int = 1,
        page_size: int = 50
    ) -> Tuple[Optional[str], List[SourceCitation], float, List[str], Dict[str, Any]]:
        """
        Executes end-to-end NLP entity extraction, database querying, ranking, and response rendering.
        Returns:
            (reply_markdown, citations_list, confidence_score, suggested_chips, debug_info)
        """
        start_time = time.perf_counter()
        entities = extract_directory_entities(query, history)

        # If query is asking conceptual/general knowledge (e.g. "What is an assistant programmer?"),
        # do not return officer directory. Return None so RAG/LLM can answer the conceptual question.
        if entities.is_general_knowledge:
            return None, [], 0.0, [], {"reason": "general_knowledge"}

        # Check Cache
        cache_key = f"{entities.normalized_query}|{entities.page}"
        now = time.time()
        if cache_key in _QUERY_CACHE:
            cached_time, cached_res = _QUERY_CACHE[cache_key]
            if now - cached_time < CACHE_TTL_SECONDS:
                logger.info(f"Officer search cache hit for '{query}'")
                return cached_res

        # Execute Multi-stage Database Matching & Ranking
        officers, match_strategy, suggestions = self.matcher.find_matching_officers(entities)
        total_count = len(officers)

        # Format Response
        reply_md, citations, chips = format_officer_response(
            officers=officers,
            entities=entities,
            total_count=total_count,
            page=entities.page or page,
            page_size=page_size,
            suggestions=suggestions
        )

        latency_ms = (time.perf_counter() - start_time) * 1000
        confidence = 1.0 if total_count > 0 or entities.is_all_departments_query else 0.85

        debug_info = {
            "query": query,
            "normalized_query": entities.normalized_query,
            "intent": entities.intent,
            "extracted_entities": {
                "name": entities.name,
                "designation": entities.designation,
                "designation_bn": entities.designation_bn,
                "department_slug": entities.department_slug,
                "department_name": entities.department_name,
                "phone": entities.phone,
                "email": entities.email,
                "page": entities.page
            },
            "match_strategy": match_strategy,
            "total_results": total_count,
            "latency_ms": round(latency_ms, 2),
            "confidence": confidence
        }

        result = (reply_md, citations, confidence, chips, debug_info)
        _QUERY_CACHE[cache_key] = (now, result)
        logger.info(f"Officer search executed for '{query}' in {latency_ms:.2f}ms (Intent: {entities.intent}, Count: {total_count})")
        return result

    def clear_cache(self):
        """Clears the in-memory query cache."""
        global _QUERY_CACHE
        _QUERY_CACHE.clear()


_service_instance: Optional[OfficerSearchService] = None


def get_officer_search_service() -> OfficerSearchService:
    global _service_instance
    if _service_instance is None:
        _service_instance = OfficerSearchService()
    return _service_instance
