"""
National University Bangladesh AI Assistant — Officer & Department Directory Search Package
"""

from .search_service import OfficerSearchService, get_officer_search_service
from .entity_extractor import OfficerQueryEntities, extract_directory_entities
from .normalizer import normalize_officer_query, normalize_text, is_general_knowledge_query
from .aliases import DESIGNATION_ALIASES, DEPARTMENT_ALIASES

__all__ = [
    "OfficerSearchService",
    "get_officer_search_service",
    "OfficerQueryEntities",
    "extract_directory_entities",
    "normalize_officer_query",
    "normalize_text",
    "is_general_knowledge_query",
    "DESIGNATION_ALIASES",
    "DEPARTMENT_ALIASES",
]
