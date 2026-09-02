"""
National University Bangladesh AI Assistant — Result Search Subsystem
"""

from .search_service import ResultSearchService, get_result_search_service
from .entity_extractor import extract_result_entities, ResultQueryEntities
from .config import RESULT_LINKS, RECENT_NOTICE_PAGE_URL, MAIN_RESULT_PORTAL

__all__ = [
    "ResultSearchService",
    "get_result_search_service",
    "extract_result_entities",
    "ResultQueryEntities",
    "RESULT_LINKS",
    "RECENT_NOTICE_PAGE_URL",
    "MAIN_RESULT_PORTAL"
]
