"""
National University AI Assistant - Autonomous 24/7 Multi-Agent Suite
"""
from .scraped_data_analyzer import ScrapedDataAnalyzerAgent, get_scraped_data_analyzer
from .knowledge_enricher import KnowledgeEnricherAgent, get_knowledge_enricher
from .knowledge_provenance import KnowledgeProvenanceAgent, get_knowledge_provenance
from .autonomous_24x7_worker import Autonomous24x7Worker, get_24x7_worker

__all__ = [
    "ScrapedDataAnalyzerAgent",
    "get_scraped_data_analyzer",
    "KnowledgeEnricherAgent",
    "get_knowledge_enricher",
    "KnowledgeProvenanceAgent",
    "get_knowledge_provenance",
    "Autonomous24x7Worker",
    "get_24x7_worker"
]
