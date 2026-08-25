import os
import sys
import unittest
import asyncio
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.crawler.db import get_db_connection, init_crawler_db
from backend.crawler.extractors import (
    normalize_url,
    compute_sha256,
    clean_extracted_text,
    classify_content,
    extract_html_page,
    extract_document_file
)
from backend.crawler.site_map import generate_website_map
from backend.crawler.deep_crawler import DeepCrawlerController
from mcp_servers.crawler_mcp import get_crawler_mcp_server
from mcp_servers.knowledge_mcp import get_knowledge_mcp_server
from mcp_servers.document_mcp import get_document_mcp_server

class TestDeepCrawlerSystem(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.test_db_path = str(PROJECT_ROOT / "data" / "test_nu_crawler.sqlite3")
        init_crawler_db(cls.test_db_path)

    def test_01_url_normalization(self):
        url1 = "https://www.nu.ac.bd/recent-notices.php?utm_source=facebook&fbclid=12345"
        norm1 = normalize_url(url1)
        self.assertEqual(norm1, "https://www.nu.ac.bd/recent-notices.php")

        url2 = "http://nu.ac.bd/admission/index.php"
        norm2 = normalize_url(url2)
        self.assertEqual(norm2, "http://www.nu.ac.bd/admission/")

        url3 = "/uploads/2026/notice_123.pdf"
        norm3 = normalize_url(url3, base_url="https://www.nu.ac.bd/notices")
        self.assertEqual(norm3, "https://www.nu.ac.bd/uploads/2026/notice_123.pdf")

    def test_02_content_classification_and_priority(self):
        sec_notice, p_type_notice, prio_notice = classify_content(
            "https://www.nu.ac.bd/recent-notices.php", "জরুরি নোটিশ ও প্রজ্ঞাপন", "২০২৬ সালের পরীক্ষার সময়সূচি"
        )
        self.assertEqual(sec_notice, "Notices")
        self.assertEqual(prio_notice, 100)

        sec_adm, p_type_adm, prio_adm = classify_content(
            "http://app1.nu.edu.bd/admission.php", "Honours Admission Circular", "Online Application Form"
        )
        self.assertEqual(sec_adm, "Admission")
        self.assertEqual(prio_adm, 95)

        sec_doc, p_type_doc, prio_doc = classify_content(
            "https://www.nu.ac.bd/uploads/syllabus_math.pdf", "syllabus.pdf", ""
        )
        self.assertEqual(sec_doc, "Documents")
        self.assertEqual(prio_doc, 85)

    def test_03_html_extraction(self):
        sample_html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Honours 4th Year Exam Routine 2026</title>
            <meta name="description" content="Official examination schedule published by Controller of Examinations.">
        </head>
        <body>
            <h1>জাতীয় বিশ্ববিদ্যালয় পরীক্ষা নোটিশ</h1>
            <p>২০২৬ সালের অনার্স ৪র্থ বর্ষ পরীক্ষার সময়সূচি প্রকাশিত হয়েছে। পরীক্ষা শুরু হবে ১৫ মার্চ ২০২৬।</p>
            <a href="/uploads/routine_2026.pdf">Download Routine PDF</a>
            <a href="https://www.nu.ac.bd/admission">Admission Portal</a>
        </body>
        </html>
        """
        parsed = extract_html_page(sample_html, url="https://www.nu.ac.bd/exam-routine.php")
        self.assertIn("Routine 2026", parsed["title"])
        self.assertIn("অনার্স ৪র্থ বর্ষ", parsed["clean_text"])
        self.assertEqual(len(parsed["links"]), 2)
        self.assertEqual(parsed["language"], "bn")
        self.assertEqual(parsed["section"], "Examination")
        self.assertTrue(len(parsed["content_hash"]) == 64)

    def test_04_document_extraction(self):
        sample_txt = "National University Notice 2026: Form Fill-up extended until 25 August 2026."
        doc_parsed = extract_document_file(sample_txt.encode("utf-8"), url="https://www.nu.ac.bd/uploads/notice.txt", content_type="text/plain")
        self.assertEqual(doc_parsed["document_type"], "TXT")
        self.assertIn("Form Fill-up extended", doc_parsed["extracted_text"])
        self.assertTrue(len(doc_parsed["content_hash"]) == 64)

    def test_05_crawler_mcp_server_tools(self):
        crawler_mcp = get_crawler_mcp_server()
        stats = crawler_mcp.get_crawl_statistics()
        self.assertIn("total_pages", stats)
        self.assertIn("total_documents", stats)

        site_map = crawler_mcp.get_website_map()
        self.assertIn("sections", site_map)
        self.assertTrue(len(site_map["sections"]) >= 8)

    def test_06_knowledge_and_document_mcp_tools(self):
        k_mcp = get_knowledge_mcp_server()
        notices_res = k_mcp.search_notices("examination", limit=3)
        self.assertTrue(notices_res["success"])

        d_mcp = get_document_mcp_server()
        docs_res = d_mcp.search_documents("notice", limit=3)
        self.assertTrue(docs_res["success"])

    def test_07_website_map_generation(self):
        s_map = generate_website_map()
        self.assertEqual(s_map["root_url"], "https://www.nu.ac.bd/")
        self.assertIn("🟢", s_map["health"])
        self.assertTrue(any(s["section"] == "Notices" for s in s_map["sections"]))
        self.assertTrue(any(s["section"] == "Admission" for s in s_map["sections"]))
        self.assertTrue(any(s["section"] == "Examination" for s in s_map["sections"]))

if __name__ == "__main__":
    unittest.main()
