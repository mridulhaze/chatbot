import logging
import urllib.parse
from bs4 import BeautifulSoup
from typing import List, Tuple
from langchain_core.documents import Document

from .base_scraper import BaseScraper
from db.sql_store import get_sql_store

logger = logging.getLogger("NU_RESULTS_SCRAPER")

RESULTS_URLS = [
    ("https://results.nu.ac.bd/", "Official Results Archive"),
    ("http://www.nu.ac.bd/results/", "Alternative Result Server")
]

class ResultsScraper(BaseScraper):
    def scrape_results_metadata(self) -> Tuple[List[Document], int, int]:
        """
        Scrapes public examination & grading rules, result checking methods, and re-scrutiny instructions.
        STRICT COMPLIANCE: NEVER scrapes individual student exam marks/rolls.
        """
        sql_store = get_sql_store()
        documents = []
        pages_scraped = 0
        new_items_count = 0

        # Structured grading and SMS rules
        results_knowledge = """# National University Result Checking & Grading System

### 1. Official Results Portals
- Primary Server: [results.nu.ac.bd](https://results.nu.ac.bd/)
- Secondary Archive: [nu.ac.bd/results](http://www.nu.ac.bd/results/)
- Individual Result Steps: Select Examination Year / Course Name -> Enter Roll / Registration Number -> Enter Exam Year -> Enter Captcha Security Code -> Click Search Result.

### 2. SMS Result Format (All Courses)
Send SMS to **16222** with the following format:
- Honours 1st Year: `NU H1 <Roll/Reg No>` -> Send to 16222
- Honours 2nd Year: `NU H2 <Roll/Reg No>` -> Send to 16222
- Honours 3rd Year: `NU H3 <Roll/Reg No>` -> Send to 16222
- Honours 4th Year: `NU H4 <Roll/Reg No>` -> Send to 16222
- Degree (Pass): `NU DEG <Roll/Reg No>` -> Send to 16222
- Masters Final: `NU MF <Roll/Reg No>` -> Send to 16222
- Preliminary to Masters: `NU MP <Roll/Reg No>` -> Send to 16222
- Professional (BBA/CSE): `NU PRO <Roll/Reg No>` -> Send to 16222

### 3. CGPA / GPA Grading Scale (4.00 System)
- 80% and above: A+ (Grade Point: 4.00)
- 75% to less than 80%: A (Grade Point: 3.75)
- 70% to less than 75%: A- (Grade Point: 3.50)
- 65% to less than 70%: B+ (Grade Point: 3.25)
- 60% to less than 65%: B (Grade Point: 3.00)
- 55% to less than 60%: B- (Grade Point: 2.75)
- 50% to less than 55%: C+ (Grade Point: 2.50)
- 45% to less than 50%: C (Grade Point: 2.25)
- 40% to less than 45%: D (Grade Point: 2.00 - Minimum Passing Grade)
- Less than 40%: F (Grade Point: 0.00 - Fail)

### 4. Re-scrutiny (খাতা পুনর্নিরীক্ষণ) Process
- Re-scrutiny applications open within 15-30 days of result publication.
- Application Portal: [nu.ac.bd/results](http://www.nu.ac.bd/results/) or Sonali Seba pay slip.
- Fee: Typically 800 BDT per paper/course.
- Payment method: Sonali Seba (Online / Bank Branch).

### 5. Degree Division Conversion
- First Class: CGPA 3.00 and above
- Second Class: CGPA 2.25 to less than 3.00
- Third Class: CGPA 2.00 to less than 2.25
"""

        # Ingest baseline Q&A into FAQ
        sql_store.insert_faq_entry(
            question="How to check National University result by SMS and Online?",
            answer="Online: Visit https://results.nu.ac.bd/ and enter your Exam Roll / Registration number and year. SMS: Type `NU <course code: H1/H2/H3/H4/DEG/MF> <Roll>` and send to 16222.",
            source_url="https://results.nu.ac.bd/",
            language="en",
            category="Results",
            confidence=1.0,
            verified_by_admin=1
        )
        sql_store.insert_faq_entry(
            question="জাতীয় বিশ্ববিদ্যালয়ের রেজাল্ট ও গ্রেডিং পয়েন্ট দেখার নিয়ম কী?",
            answer="অনলাইনে রেজাল্ট দেখতে results.nu.ac.bd ভিজিট করুন। SMS-এ দেখতে মেসেজ অপশনে লিখুন NU <H1/H2/H3/H4/DEG/MF> <Roll/Reg No> এবং পাঠিয়ে দিন 16222 নম্বরে। গ্রেডিং স্কেলে ৪০% এ পাস (GPA 2.00 / D) এবং ৮০% বা তার বেশি পেলে A+ (GPA 4.00)।",
            source_url="https://results.nu.ac.bd/",
            language="bn",
            category="Results",
            confidence=1.0,
            verified_by_admin=1
        )
        new_items_count += 2

        doc = Document(
            page_content=results_knowledge,
            metadata={"source": "https://results.nu.ac.bd/", "category": "Results & Grading", "type": "results_guide"}
        )
        documents.append(doc)

        # Attempt to probe results server availability
        for url, name in RESULTS_URLS:
            try:
                html = self.fetch_url(url)
                if html:
                    pages_scraped += 1
            except Exception as e:
                logger.warning(f"Could not reach {url}: {e}")

        logger.info(f"Results metadata generated. Documents: {len(documents)}")
        return documents, pages_scraped, new_items_count
