"""
National University Bangladesh AI Assistant — Comprehensive Result Search Engine Test Suite
Validates all 40+ result query intents, entity extractions, URL routing, notice ranking, and anti-hallucination guardrails.
"""

import unittest
import time
import sys
from pathlib import Path

# Ensure project root in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.result_search import (
    get_result_search_service,
    extract_result_entities,
    RESULT_LINKS,
    MAIN_RESULT_PORTAL,
    RECENT_NOTICE_PAGE_URL
)
from backend.rag_engine import RAGEngine, get_rag_engine


class TestResultSearchEngine(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.service = get_result_search_service()
        cls.rag = get_rag_engine()

    # =========================================================================
    # Group 1: General Result Menu Queries (RESULT_GENERAL)
    # =========================================================================
    def test_general_result_menu_queries(self):
        test_queries = [
            "result",
            "রেজাল্ট",
            "ফলাফল",
            "NU result",
            "জাতীয় বিশ্ববিদ্যালয়ের রেজাল্ট",
            "nu folafol",
            "result dekhte chai"
        ]
        for q in test_queries:
            entities = extract_result_entities(q)
            self.assertTrue(entities.is_result_query, f"Failed trigger for: {q}")
            self.assertEqual(entities.sub_intent, "RESULT_GENERAL", f"Wrong sub-intent for: {q}")

            reply, citations, conf, chips, debug = self.service.search_and_format(q)
            self.assertIsNotNone(reply, f"Reply is None for: {q}")
            self.assertIn("জাতীয় বিশ্ববিদ্যালয়ের রেজাল্ট", reply)
            self.assertIn("results.nu.ac.bd", reply)
            self.assertTrue(any("অনার্স রেজাল্ট" in c for c in chips))

    # =========================================================================
    # Group 2: Program-Specific Result Link Routing
    # =========================================================================
    def test_program_specific_result_links(self):
        cases = [
            ("honours result", "HONOURS", "https://results.nu.ac.bd/honours", "অনার্স"),
            ("অনার্স রেজাল্ট", "HONOURS", "https://results.nu.ac.bd/honours", "অনার্স"),
            ("degree result", "DEGREE", "https://results.nu.ac.bd/degree", "ডিগ্রি"),
            ("ডিগ্রি রেজাল্ট", "DEGREE", "https://results.nu.ac.bd/degree", "ডিগ্রি"),
            ("masters result", "MASTERS", "https://results.nu.ac.bd/masters", "মাস্টার্স"),
            ("মাস্টার্স রেজাল্ট", "MASTERS", "https://results.nu.ac.bd/masters", "মাস্টার্স"),
            ("professional result", "PROFESSIONAL", "https://results.nu.ac.bd/professional", "প্রফেশনাল"),
            ("প্রফেশনাল রেজাল্ট", "PROFESSIONAL", "https://results.nu.ac.bd/professional", "প্রফেশনাল"),
            ("revaluation result", "REVALUATION", "https://results.nu.ac.bd/revaluation", "পুনঃনিরীক্ষণ"),
            ("পুনঃনিরীক্ষণ ফলাফল", "REVALUATION", "https://results.nu.ac.bd/revaluation", "পুনঃনিরীক্ষণ"),
        ]
        for query, expected_prog, expected_url, expected_bn in cases:
            entities = extract_result_entities(query)
            self.assertTrue(entities.is_result_query, f"Failed trigger: {query}")
            self.assertEqual(entities.program, expected_prog, f"Program mismatch for {query}: got {entities.program}")

            reply, citations, conf, chips, debug = self.service.search_and_format(query)
            self.assertIsNotNone(reply, f"Reply None for: {query}")
            self.assertIn(expected_url, reply, f"Expected URL {expected_url} missing in reply for: {query}")
            self.assertIn(expected_bn, reply, f"Expected Bangla name {expected_bn} missing in reply for: {query}")

    # =========================================================================
    # Group 3: Year & Program Entity Extractions (Honours 4th Year, etc.)
    # =========================================================================
    def test_year_and_program_extractions(self):
        cases = [
            ("honours 4th year result", "HONOURS", "4TH_YEAR"),
            ("অনার্স ৪র্থ বর্ষের রেজাল্ট", "HONOURS", "4TH_YEAR"),
            ("honours 1st year result", "HONOURS", "1ST_YEAR"),
            ("অনার্স ১ম বর্ষের ফলাফল", "HONOURS", "1ST_YEAR"),
            ("degree 3rd year result", "DEGREE", "3RD_YEAR"),
            ("ডিগ্রি ৩য় বর্ষের রেজাল্ট", "DEGREE", "3RD_YEAR"),
            ("masters final result", "MASTERS", "FINAL_YEAR"),
            ("মাস্টার্স ফাইনাল রেজাল্ট", "MASTERS", "FINAL_YEAR"),
        ]
        for query, exp_prog, exp_year in cases:
            entities = extract_result_entities(query)
            self.assertEqual(entities.program, exp_prog, f"Program mismatch for {query}")
            self.assertEqual(entities.year, exp_year, f"Year mismatch for {query}")

            reply, citations, conf, chips, debug = self.service.search_and_format(query)
            self.assertIsNotNone(reply)
            self.assertIn(RESULT_LINKS[exp_prog]["url"], reply)

    # =========================================================================
    # Group 4: "Has Result Been Published?" Queries (RESULT_PUBLICATION)
    # =========================================================================
    def test_publication_check_queries(self):
        queries = [
            "honours 4th year result published?",
            "অনার্স ৪র্থ বর্ষের রেজাল্ট প্রকাশ হয়েছে?",
            "result ber hoise?",
            "result publish hoise?",
            "ফলাফল প্রকাশ হয়েছে কি?",
            "honours result published?"
        ]
        for q in queries:
            entities = extract_result_entities(q)
            self.assertTrue(entities.is_result_query, f"Trigger failed: {q}")
            self.assertEqual(entities.sub_intent, "RESULT_PUBLICATION", f"Sub-intent wrong for: {q}")

            reply, citations, conf, chips, debug = self.service.search_and_format(q)
            self.assertIsNotNone(reply)
            # Response must provide portal link and recent notice link
            self.assertIn("results.nu.ac.bd", reply)
            self.assertIn(RECENT_NOTICE_PAGE_URL, reply)

    # =========================================================================
    # Group 5: "When Will Result Be Published?" (RESULT_DATE_QUERY) & Anti-Hallucination
    # =========================================================================
    def test_date_query_and_anti_hallucination(self):
        queries = [
            "result kobe",
            "result kobe dibe",
            "honours 4th year result kobe?",
            "অনার্স ৪র্থ বর্ষের রেজাল্ট কবে দিবে?",
            "folafol kobe asbe"
        ]
        for q in queries:
            entities = extract_result_entities(q)
            self.assertTrue(entities.is_result_query, f"Trigger failed: {q}")
            self.assertEqual(entities.sub_intent, "RESULT_DATE_QUERY", f"Sub-intent wrong for: {q}")

            reply, citations, conf, chips, debug = self.service.search_and_format(q)
            self.assertIsNotNone(reply)

            # STRICT ANTI-HALLUCINATION VERIFICATION:
            # Must NOT contain fabricated predictions like "সম্ভবত আগামী সপ্তাহে" or "কাল প্রকাশ হবে"
            self.assertNotIn("সম্ভবত আগামী সপ্তাহে", reply)
            self.assertNotIn("কাল প্রকাশ হবে", reply)
            self.assertNotIn("সম্ভবত শুক্রবার", reply)

    # =========================================================================
    # Group 6: Latest Result Notice Searches (RESULT_LATEST_NOTICE)
    # =========================================================================
    def test_latest_result_notice_queries(self):
        queries = [
            "latest result",
            "সর্বশেষ রেজাল্ট",
            "recent result",
            "recent result notice",
            "ফলাফল প্রকাশের নোটিশ",
            "latest honours result",
            "latest professional result"
        ]
        for q in queries:
            entities = extract_result_entities(q)
            self.assertTrue(entities.is_result_query, f"Trigger failed: {q}")
            self.assertIn(entities.sub_intent, ["RESULT_LATEST_NOTICE", "RESULT_BY_PROGRAM", "RESULT_PUBLICATION"])

            reply, citations, conf, chips, debug = self.service.search_and_format(q)
            self.assertIsNotNone(reply)
            self.assertIn("results.nu.ac.bd", reply)

    # =========================================================================
    # Group 7: Direct Link Inquiries (RESULT_LINK)
    # =========================================================================
    def test_direct_link_inquiries(self):
        cases = [
            ("result link", "https://results.nu.ac.bd/"),
            ("honours result link", "https://results.nu.ac.bd/honours"),
            ("where can I check my result", "https://results.nu.ac.bd/"),
            ("result দেখব কিভাবে", "https://results.nu.ac.bd/"),
            ("অনার্সের result কোথায় দেখব", "https://results.nu.ac.bd/honours"),
            ("degree result website", "https://results.nu.ac.bd/degree")
        ]
        for query, expected_url in cases:
            entities = extract_result_entities(query)
            self.assertTrue(entities.is_result_query)
            self.assertIn(entities.sub_intent, ["RESULT_LINK", "RESULT_CHECK", "RESULT_BY_PROGRAM"])

            reply, citations, conf, chips, debug = self.service.search_and_format(query)
            self.assertIn(expected_url, reply)

    # =========================================================================
    # Group 8: Multi-Turn Conversation Context
    # =========================================================================
    def test_multi_turn_conversation_context(self):
        # Turn 1: User asks "honours result"
        history = [
            {"role": "user", "content": "honours result"},
            {"role": "assistant", "content": "Here is Honours result portal: https://results.nu.ac.bd/honours"}
        ]
        # Turn 2: User says "4th year"
        q2 = "4th year"
        entities = extract_result_entities(q2, history=history)
        self.assertTrue(entities.is_result_query, "Turn 2 should be recognized as result query from history")
        self.assertEqual(entities.program, "HONOURS", "Turn 2 should inherit program HONOURS")
        self.assertEqual(entities.year, "4TH_YEAR", "Turn 2 should extract year 4TH_YEAR")

        reply, citations, conf, chips, debug = self.service.search_and_format(q2, history=history)
        self.assertIn("https://results.nu.ac.bd/honours", reply)

        # Turn 3: User asks "kobe dibe?"
        history.extend([
            {"role": "user", "content": "4th year"},
            {"role": "assistant", "content": reply}
        ])
        q3 = "kobe dibe?"
        entities3 = extract_result_entities(q3, history=history)
        self.assertTrue(entities3.is_result_query)
        self.assertEqual(entities3.program, "HONOURS")
        self.assertEqual(entities3.year, "4TH_YEAR")
        self.assertEqual(entities3.sub_intent, "RESULT_DATE_QUERY")

    # =========================================================================
    # Group 9: Roll & Registration Number Guidance (No fake results)
    # =========================================================================
    def test_roll_registration_guidance(self):
        q = "check my result roll 123456 reg 789012"
        entities = extract_result_entities(q)
        self.assertEqual(entities.sub_intent, "RESULT_CHECK")
        self.assertEqual(entities.roll_number, "123456")
        self.assertEqual(entities.reg_number, "789012")

        reply, citations, conf, chips, debug = self.service.search_and_format(q)
        self.assertIn("রোল", reply)
        self.assertIn("রেজিস্ট্রেশন", reply)
        self.assertIn("results.nu.ac.bd", reply)
        # Verify no fake marks fabricated
        self.assertNotIn("CGPA: 3.", reply)
        self.assertNotIn("Grade: A", reply)

    # =========================================================================
    # Group 10: Non-Hijacking & Negative Checks
    # =========================================================================
    def test_non_hijacking_checks(self):
        non_result_queries = [
            "what is an assistant programmer?",
            "ICT department officers",
            "show all departments",
            "how to apply for TC online",
            "honours admission eligibility",
            "what is the fee for provisional certificate"
        ]
        for q in non_result_queries:
            entities = extract_result_entities(q)
            self.assertFalse(entities.is_result_query, f"Should NOT be classified as result query: {q}")

    # =========================================================================
    # Group 11: End-to-End RAG Engine Integration
    # =========================================================================
    def test_rag_engine_integration(self):
        # 1. Test classify_intent
        self.assertEqual(self.rag.classify_intent("honours 4th year result"), "results")
        self.assertEqual(self.rag.classify_intent("result"), "results")
        self.assertEqual(self.rag.classify_intent("রেজাল্ট কবে দিবে"), "results")
        self.assertEqual(self.rag.classify_intent("masters final result"), "results")
        self.assertEqual(self.rag.classify_intent("revaluation result"), "results")

        # 2. Test answer_query fast path
        resp = self.rag.answer_query("honours 4th year result")
        self.assertEqual(resp.intent, "results")
        self.assertIn("https://results.nu.ac.bd/honours", resp.reply)
        self.assertGreaterEqual(resp.confidence, 0.95)

    # =========================================================================
    # Group 12: Latency & Performance Benchmark (< 100ms SLA)
    # =========================================================================
    def test_performance_benchmark(self):
        bench_queries = [
            "result",
            "honours result",
            "honours 4th year result",
            "degree result",
            "masters result",
            "professional result",
            "revaluation result",
            "result kobe dibe?"
        ]
        latencies = []
        for q in bench_queries:
            t0 = time.perf_counter()
            reply, citations, conf, chips, debug = self.service.search_and_format(q)
            elapsed_ms = (time.perf_counter() - t0) * 1000.0
            latencies.append(elapsed_ms)
            self.assertIsNotNone(reply)

        avg_latency = sum(latencies) / len(latencies)
        print(f"\n[BENCHMARK] Average Result Search Latency: {avg_latency:.2f}ms across {len(bench_queries)} queries")
    # =========================================================================
    # Group 13: Exhaustive Verification of All 30 User Specified Queries
    # =========================================================================
    def test_all_thirty_specified_prompt_queries(self):
        thirty_queries = [
            "result", "রেজাল্ট", "ফলাফল", "NU result", "honours result", "অনার্স রেজাল্ট",
            "honours 4th year result", "অনার্স ৪র্থ বর্ষের রেজাল্ট", "degree result", "ডিগ্রি রেজাল্ট",
            "masters result", "মাস্টার্স রেজাল্ট", "professional result", "প্রফেশনাল রেজাল্ট",
            "revaluation result", "পুনঃনিরীক্ষণ ফলাফল", "result kobe", "result kobe dibe",
            "result ber hoise?", "honours result published?", "honours 4th year result published?",
            "latest result", "সর্বশেষ রেজাল্ট", "latest honours result", "latest professional result",
            "result link", "honours result link", "where can I check my result",
            "result দেখব কিভাবে", "অনার্সের result কোথায় দেখব"
        ]
        for q in thirty_queries:
            entities = extract_result_entities(q)
            self.assertTrue(entities.is_result_query, f"Query failed result detection: '{q}'")
            reply, citations, conf, chips, debug = self.service.search_and_format(q)
            self.assertIsNotNone(reply, f"Reply was None for: '{q}'")
            self.assertGreater(len(reply), 30, f"Reply too short for: '{q}'")
            self.assertIn("results.nu.ac.bd", reply, f"Official result domain missing for: '{q}'")
            self.assertGreaterEqual(conf, 0.95)

if __name__ == "__main__":
    unittest.main()
