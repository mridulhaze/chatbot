"""Crawler package for National University AI Assistant."""
from .base_scraper import BaseScraper
from .notices_scraper import NoticesScraper
from .admission_scraper import AdmissionScraper
from .results_scraper import ResultsScraper
from .ems_scraper import EMSScraper
from .ict_scraper import ICTScraper
from .departments_scraper import DepartmentsScraper
from .homepage_scraper import HomepageScraper
from .scheduler import run_full_crawl, start_scheduler, stop_scheduler, get_crawler_status
from .deep_crawler_bridge import run_deep_crawler, get_deep_crawler_status

__all__ = [
    "BaseScraper",
    "NoticesScraper",
    "AdmissionScraper",
    "ResultsScraper",
    "EMSScraper",
    "ICTScraper",
    "DepartmentsScraper",
    "HomepageScraper",
    "run_full_crawl",
    "start_scheduler",
    "stop_scheduler",
    "get_crawler_status",
    "run_deep_crawler",
    "get_deep_crawler_status"
]
