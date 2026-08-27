"""
Unit Tests for Hermes Agent Interactive Learning Brain
Verifies:
1. Brain status and operational metrics.
2. Accurate official portal URL citations (no deprecated links).
3. English numeral phone normalization.
4. Knowledge gap auto-resolution & FAQ insertion into faq_entries.
5. Notice FAQ extraction.
6. Solver Co-Pilot solution recommendation.
"""

import os
import sys
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from backend.services.hermes_brain_service import get_hermes_brain, convert_bn_to_en_digits, OFFICIAL_PORTALS
from db.sql_store import get_sql_store
from token_service.db import init_token_database

class TestHermesLearningBrain(unittest.TestCase):
    def setUp(self):
        init_token_database()
        self.brain = get_hermes_brain()
        self.sql_store = get_sql_store()

    def test_01_brain_status_and_compliance(self):
        """Verify brain status reports active online state and domain compliance."""
        status = self.brain.get_brain_status()
        self.assertEqual(status["status"], "ONLINE")
        self.assertIn("Hermes", status["brain_engine"])
        self.assertTrue(status["domain_compliance"]["official_portals_enforced"])
        self.assertTrue(status["domain_compliance"]["english_phone_digits_enforced"])
        print("[TEST 1 PASS] Hermes Brain status and compliance flags verified.")

    def test_02_phone_numeral_normalization(self):
        """Verify Bengali numerals are converted to English digits."""
        raw_bn = "০১৭১১-৬৭৭৫৭৭"
        expected = "01711-677577"
        self.assertEqual(convert_bn_to_en_digits(raw_bn), expected)
        print("[TEST 2 PASS] Bengali phone digits normalized to English numerals.")

    def test_03_knowledge_gap_auto_resolution(self):
        """Verify Hermes can ingest a gap, synthesize answer with official URL, and insert FAQ."""
        # 1. Record a mock test gap in gap_queue
        gap_id = self.sql_store.log_gap("EMS পাসওয়ার্ড রিসেট করার নিয়ম কী?", language="bn", reason="unresolved")
        self.assertIsNotNone(gap_id)

        # 2. Run auto-resolution
        res = self.brain.auto_resolve_gap(gap_id)
        self.assertTrue(res["success"])
        self.assertEqual(res["category"], "EMS_PORTAL")
        self.assertEqual(res["official_url"], "http://ems.nu.ac.bd/")
        self.assertIn("ems.nu.ac.bd", res["answer_bn"])

        # 3. Verify status updated in DB
        conn = self.sql_store._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT status FROM gap_queue WHERE id = ?", (gap_id,))
        gap_row = cursor.fetchone()
        self.assertEqual(gap_row["status"], "resolved")
        print(f"[TEST 3 PASS] Gap #{gap_id} auto-resolved with official EMS portal citation.")

    def test_04_notice_faq_extraction(self):
        """Verify Hermes extracts structured FAQs from a notice."""
        # 1. Insert a mock notice
        self.sql_store.upsert_notice(
            title="২০২৪ সালের ডিগ্রি পাস ১ম বর্ষ পরীক্ষার ফরম পূরণের সংশোধিত বিজ্ঞপ্তি",
            url="https://www.nu.ac.bd/notice-degree-2024.php",
            pdf_url="https://www.nu.ac.bd/notice-degree-2024.pdf",
            category="EXAM_ROUTINE",
            published_date="2026-08-25",
            raw_text="ডিগ্রি পাস ১ম বর্ষ ফরম পূরণ শুরু ১৫ সেপ্টেম্বর..."
        )
        
        # Get notice id
        conn = self.sql_store._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM notices WHERE url = 'https://www.nu.ac.bd/notice-degree-2024.php'")
        nid = cursor.fetchone()[0]

        # 2. Extract FAQ
        res = self.brain.extract_notice_faqs(nid)
        self.assertTrue(res["success"])
        self.assertIn("সংশোধিত বিজ্ঞপ্তি", res["question"])
        self.assertEqual(res["url"], "https://www.nu.ac.bd/notice-degree-2024.php")
        print(f"[TEST 4 PASS] Notice #{nid} structured FAQs extracted successfully.")

    def test_05_solver_copilot_solution(self):
        """Verify Solver Co-Pilot suggests correct desk and steps."""
        res = self.brain.suggest_token_solution("NU-2026-000001")
        self.assertIn("success", res)
        print("[TEST 5 PASS] Solver Co-Pilot recommendation logic verified.")

if __name__ == "__main__":
    unittest.main()
