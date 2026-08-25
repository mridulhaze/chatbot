import re
import logging
import urllib.parse
from bs4 import BeautifulSoup
from typing import List, Tuple, Dict, Any
from langchain_core.documents import Document

from .base_scraper import BaseScraper
from db.sql_store import get_sql_store

logger = logging.getLogger("NU_HOMEPAGE_SCRAPER")

class HomepageScraper(BaseScraper):
    """
    Crawls and parses https://www.nu.ac.bd/ home page and all major category links:
    - Governance & Leadership
    - Academic Programs & Faculties
    - Quick Links & Portals
    - Latest Events & News
    - Syllabi & Academic Calendar
    """
    HOME_URL = "https://www.nu.ac.bd/"

    CATEGORY_PAGES = [
        {"category": "Academic Calendar", "url": "https://www.nu.ac.bd/academic-calendar-list.php", "type": "academic_calendar"},
        {"category": "Honours Syllabus", "url": "https://www.nu.ac.bd/syllabus-honours.php", "type": "syllabus"},
        {"category": "Degree Pass Syllabus", "url": "https://www.nu.ac.bd/syllabus-degree-pass.php", "type": "syllabus"},
        {"category": "Masters Syllabus", "url": "https://www.nu.ac.bd/syllabus-masters.php", "type": "syllabus"},
        {"category": "Professional Syllabus", "url": "https://www.nu.ac.bd/syllabus-professional.php", "type": "syllabus"},
        {"category": "Latest News & Events", "url": "https://www.nu.ac.bd/latest-news.php", "type": "events"},
        {"category": "Faculty Information", "url": "https://www.nu.ac.bd/faculty-social-science.php", "type": "faculty"},
        {"category": "General FAQ", "url": "https://www.nu.ac.bd/faq.php", "type": "faq"}
    ]

    def scrape_homepage_and_categories(self) -> Tuple[List[Document], int, int]:
        all_docs: List[Document] = []
        pages_scraped = 0
        new_items = 0

        # 1. Scrape Homepage structure
        home_html = self.fetch_url(self.HOME_URL)
        if home_html:
            pages_scraped += 1
            soup = BeautifulSoup(home_html, "html.parser")
            for tag in soup(["script", "style", "noscript", "svg"]):
                tag.decompose()

            # A. Extract Navbar Categorized Links
            navbar_data: Dict[str, List[Dict[str, str]]] = {}
            for li in soup.find_all("li"):
                header = li.find(["a", "span", "h3"])
                header_text = header.get_text(strip=True) if header else ""
                if header_text in ["About", "Governance", "Administration", "Academic", "Office", "Notice", "Admission", "Training", "Publications", "Services"]:
                    links = []
                    for sub_a in li.find_all("a", href=True):
                        txt = sub_a.get_text(" ", strip=True)
                        h = sub_a['href'].strip()
                        if h and not h.startswith('#') and not h.startswith('javascript:'):
                            full_h = urllib.parse.urljoin(self.HOME_URL, h)
                            links.append({"title": txt, "url": full_h})
                    if links:
                        navbar_data[header_text] = links

            nav_summary = "# জাতীয় বিশ্ববিদ্যালয় অফিশিয়াল পোর্টাল মেনু ও ক্যাটাগরি ডিরেক্টরি (Official Portal Navigation Hierarchy)\n\n"
            for cat, items in navbar_data.items():
                nav_summary += f"### {cat} Menu:\n"
                for itm in items:
                    nav_summary += f"- [{itm['title']}]({itm['url']})\n"
                nav_summary += "\n"

            all_docs.append(Document(
                page_content=nav_summary,
                metadata={"source": self.HOME_URL, "category": "Navigation & Categories", "type": "homepage_navigation"}
            ))

            # B. Extract Homepage Events & News
            events_section = []
            for ev in soup.find_all(class_=lambda c: c and any(k in str(c).lower() for k in ["event", "news", "announcement", "headline"])):
                ev_txt = ev.get_text(" ", strip=True)
                if len(ev_txt) > 25 and ev_txt not in events_section:
                    events_section.append(ev_txt)

            if events_section:
                ev_summary = "# জাতীয় বিশ্ববিদ্যালয় সর্বশেষ সংবাদ ও ইভেন্ট (Latest News & Events from Homepage)\n\n"
                for ev_t in events_section[:20]:
                    ev_summary += f"- {ev_t}\n"
                all_docs.append(Document(
                    page_content=ev_summary,
                    metadata={"source": self.HOME_URL, "category": "News & Events", "type": "homepage_events"}
                ))

        # 2. Scrape Specific Category Pages
        for page_info in self.CATEGORY_PAGES:
            p_url = page_info["url"]
            p_cat = page_info["category"]
            p_type = page_info["type"]

            p_html = self.fetch_url(p_url)
            if not p_html:
                continue

            pages_scraped += 1
            p_soup = BeautifulSoup(p_html, "html.parser")
            for tag in p_soup(["script", "style", "noscript"]):
                tag.decompose()

            # Extract main content / table rows
            content_lines = []
            for tr in p_soup.find_all("tr"):
                cols = [td.get_text(" ", strip=True) for td in tr.find_all(["td", "th"])]
                if cols and len(" ".join(cols)) > 10:
                    content_lines.append(" | ".join(cols))

            if not content_lines:
                for p in p_soup.find_all(["p", "div", "li"]):
                    txt = p.get_text(" ", strip=True)
                    if len(txt) > 40 and txt not in content_lines:
                        content_lines.append(txt)

            if content_lines:
                cat_doc_text = f"# জাতীয় বিশ্ববিদ্যালয় — {p_cat}\n"
                cat_doc_text += f"অফিসিয়াল লিংক: {p_url}\n\n"
                cat_doc_text += "\n".join(content_lines[:35])

                all_docs.append(Document(
                    page_content=cat_doc_text,
                    metadata={"source": p_url, "category": p_cat, "type": p_type}
                ))
                new_items += 1

        logger.info(f"Homepage & Categories scraping completed. Pages: {pages_scraped}, Docs created: {len(all_docs)}")
        return all_docs, pages_scraped, new_items
