"""
National University Bangladesh AI Assistant — Result Search Service
Main facade orchestrating entity extraction, notice search, ranking, and response formatting for results.
"""

import time
import logging
from typing import Dict, Any, List, Optional, Tuple

from .entity_extractor import extract_result_entities, ResultQueryEntities
from .notice_searcher import ResultNoticeSearcher
from .formatter import format_result_response
from backend.models import SourceCitation

logger = logging.getLogger("NU_RESULT_SEARCH_SERVICE")

_RESULT_SEARCH_SERVICE_INSTANCE = None


class ResultSearchService:
    def __init__(self):
        self.notice_searcher = ResultNoticeSearcher()

    def is_result_query(self, query: str, history: Optional[List[Any]] = None) -> bool:
        """
        Determines whether a user query should be handled by the Result Search Engine.
        """
        if not query or not query.strip():
            return False
        entities = extract_result_entities(query, history)
        return entities.is_result_query

    def search_and_format(
        self,
        query: str,
        history: Optional[List[Any]] = None
    ) -> Tuple[Optional[str], List[SourceCitation], float, List[str], Dict[str, Any]]:
        """
        Processes a result inquiry, searches recent official result notices, and formats the response.
        Returns: (reply_markdown, citations, confidence, action_chips, debug_metadata)
        """
        start_time = time.perf_counter()

        entities = extract_result_entities(query, history)
        if not entities.is_result_query:
            return None, [], 0.0, [], {"is_result_query": False}

        # Search recent matching notices
        notices = self.notice_searcher.search_result_notices(entities, limit=3)

        # Format output
        reply_md, citations, confidence, action_chips = format_result_response(entities, notices)

        elapsed_ms = (time.perf_counter() - start_time) * 1000.0

        debug_metadata = {
            "sub_intent": entities.sub_intent,
            "program": entities.program,
            "year": entities.year,
            "total_notices_found": len(notices),
            "latency_ms": round(elapsed_ms, 2)
        }

        return reply_md, citations, confidence, action_chips, debug_metadata


def get_result_search_service() -> ResultSearchService:
    global _RESULT_SEARCH_SERVICE_INSTANCE
    if _RESULT_SEARCH_SERVICE_INSTANCE is None:
        _RESULT_SEARCH_SERVICE_INSTANCE = ResultSearchService()
    return _RESULT_SEARCH_SERVICE_INSTANCE
