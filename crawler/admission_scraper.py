import logging
import urllib.parse
from bs4 import BeautifulSoup
from typing import List, Tuple
from langchain_core.documents import Document

from .base_scraper import BaseScraper
from db.sql_store import get_sql_store

logger = logging.getLogger("NU_ADMISSION_SCRAPER")

ADMISSION_URLS = [
    ("http://app1.nu.edu.bd/", "Main Admission Portal"),
    ("https://www.nu.ac.bd/admission-notice.php", "Admission Notices")
]

class AdmissionScraper(BaseScraper):
    def scrape_admissions(self) -> Tuple[List[Document], int, int]:
        sql_store = get_sql_store()
        documents = []
        pages_scraped = 0
        new_items_count = 0

        # Baseline admission guidelines structured knowledge
        baseline_programs = [
            {
                "program": "Honours 1st Year Admission",
                "level": "Undergraduate",
                "eligibility": "SSC minimum GPA 3.0 / 3.5 and HSC minimum GPA 3.0 / 3.5 depending on Humanities/Science/Business.",
                "deadline": "See active circular on app1.nu.edu.bd",
                "notes": "Application is 100% online via app1.nu.edu.bd. Merit list prepared on combined SSC (40%) + HSC (60%) GPA. 1st Merit List, 2nd Merit List, Quota Merit List, and 2 Release Slips.",
                "source_url": "http://app1.nu.edu.bd/"
            },
            {
                "program": "Degree (Pass) 1st Year Admission",
                "level": "Undergraduate",
                "eligibility": "SSC minimum GPA 2.0 and HSC minimum GPA 2.0 from recognized boards.",
                "deadline": "As per official schedule",
                "notes": "Admission through online application at app1.nu.edu.bd under Degree Pass tab.",
                "source_url": "http://app1.nu.edu.bd/"
            },
            {
                "program": "Masters (Regular) Admission",
                "level": "Postgraduate",
                "eligibility": "Honours 4-year degree with minimum CGPA 2.25 or Degree (Pass) + Preliminary to Masters.",
                "deadline": "Announced annually after Honours 4th year results.",
                "notes": "Online application, college verification, merit list based on Honours CGPA.",
                "source_url": "http://app1.nu.edu.bd/"
            },
            {
                "program": "Honours Professional Admission (BBA/CSE/ECE/THM/Fashion)",
                "level": "Professional Undergraduate",
                "eligibility": "HSC passed with required GPA (min 2.50 to 3.00 depending on department).",
                "deadline": "Published on official notice board",
                "notes": "Courses offered at affiliated professional institutes.",
                "source_url": "http://app1.nu.edu.bd/"
            }
        ]

        for prog in baseline_programs:
            sql_store.upsert_admission_info(
                program=prog["program"],
                level=prog["level"],
                eligibility=prog["eligibility"],
                deadline=prog["deadline"],
                notes=prog["notes"],
                source_url=prog["source_url"]
            )
            new_items_count += 1

        # Now attempt to scrape live circulars from app1.nu.edu.bd or nu.ac.bd/admission-notice.php
        for url, name in ADMISSION_URLS:
            html = self.fetch_url(url)
            if not html:
                continue
            pages_scraped += 1
            soup = BeautifulSoup(html, "html.parser")
            
            # Extract links and text
            links = []
            for a in soup.find_all("a", href=True):
                text = a.get_text(strip=True)
                href = urllib.parse.urljoin(url, a["href"])
                if any(w in text.lower() for w in ["admission", "ভর্তি", "circular", "guideline", "notice", "release slip", "merit"]):
                    links.append(f"- [{text}]({href})")

            page_text = self.clean_text(soup.get_text())
            if page_text:
                doc_content = f"# National University Admission Guide & Portal Updates ({name})\n\n"
                doc_content += f"Portal URL: {url}\n\n"
                doc_content += "### Key Circulars & Links:\n" + "\n".join(links[:20]) + "\n\n"
                doc_content += "### Admission Overview & General Rules:\n"
                for p in baseline_programs:
                    doc_content += f"#### {p['program']} ({p['level']})\n"
                    doc_content += f"- **Eligibility**: {p['eligibility']}\n"
                    doc_content += f"- **Application & Merit Rules**: {p['notes']}\n"
                    doc_content += f"- **Portal**: {p['source_url']}\n\n"

                documents.append(Document(page_content=doc_content, metadata={"source": url, "category": "Admission"}))

        logger.info(f"Admission scraping completed. Pages: {pages_scraped}, Items: {new_items_count}")
        return documents, pages_scraped, new_items_count
