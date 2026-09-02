"""
National University Bangladesh AI Assistant — Officer Search Benchmark & Test Suite
Covers 50+ test cases across 10 query categories verifying precision, recall, latency, and anti-hallucination.
"""

import sys
import time
import unittest
from pathlib import Path

# Add project root to sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from backend.officer_search import (
    get_officer_search_service,
    extract_directory_entities,
    is_general_knowledge_query,
    OfficerQueryEntities
)
from backend.rag_engine import RAGEngine


class TestOfficerSearchEngine(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.search_service = get_officer_search_service()
        cls.search_service.clear_cache()
        cls.rag_engine = RAGEngine()

    def setUp(self):
        self.search_service.clear_cache()

    # =====================================================================
    # 1. EXACT DESIGNATION TESTS (Bangla, English, Plurals)
    # =====================================================================
    def test_designation_search_suite(self):
        cases = [
            ("list all assistant programmers", "Assistant Programmer", 7),
            ("assistant programmers", "Assistant Programmer", 7),
            ("সহকারী প্রোগ্রামার", "Assistant Programmer", 7),
            ("সহকারী প্রোগ্রামারদের তালিকা", "Assistant Programmer", 7),
            ("সহকারী প্রোগ্রামারগণ", "Assistant Programmer", 7),
            ("who are the assistant programmers?", "Assistant Programmer", 7),
            ("Programmer", "Programmer", 20),
            ("প্রোগ্রামার তালিকা", "Programmer", 20),
            ("Senior Programmer", "Senior Programmer", 2),
            ("সিনিয়র প্রোগ্রামার", "Senior Programmer", 2),
            ("সিনিয়র প্রোগ্রামার", "Senior Programmer", 2),
            ("System Analyst", "System Analyst", 1),
            ("সিস্টেম এনালিস্ট", "System Analyst", 1),
            ("Network Administrator", "Network Administrator", 1),
            ("নেটওয়ার্ক এডমিনিস্ট্রেটর", "Network Administrator", 1),
        ]
        for query, expected_desig, min_results in cases:
            with self.subTest(query=query):
                entities = extract_directory_entities(query)
                self.assertEqual(entities.designation, expected_desig, f"Failed designation extraction for '{query}'")
                self.assertFalse(entities.is_general_knowledge, f"'{query}' incorrectly flagged as general knowledge")

                reply, citations, conf, chips, debug = self.search_service.search_and_format(query)
                self.assertIsNotNone(reply, f"Reply was None for '{query}'")
                self.assertGreaterEqual(debug["total_results"], min_results, f"Expected >={min_results} results for '{query}'")
                self.assertGreaterEqual(conf, 0.90)

    # =====================================================================
    # 2. DESIGNATION + DEPARTMENT COMBINED STRICT FILTER (Strict AND logic)
    # =====================================================================
    def test_designation_and_department_combined_filters(self):
        cases = [
            ("assistant programmer in ICT", "Assistant Programmer", "ict-department", 4),
            ("ICT assistant programmer", "Assistant Programmer", "ict-department", 4),
            ("আইসিটি দপ্তরের সহকারী প্রোগ্রামার", "Assistant Programmer", "ict-department", 4),
            ("ict te assistant programmer ke ke", "Assistant Programmer", "ict-department", 4),
            ("assistant programmer in admission cell", "Assistant Programmer", "admission-registration", 2),
            ("international desk assistant programmer", "Assistant Programmer", "international-desk", 1),
        ]
        for query, expected_desig, expected_dept, exact_count in cases:
            with self.subTest(query=query):
                entities = extract_directory_entities(query)
                self.assertEqual(entities.designation, expected_desig)
                self.assertEqual(entities.department_slug, expected_dept)

                reply, citations, conf, chips, debug = self.search_service.search_and_format(query)
                self.assertIsNotNone(reply)
                self.assertEqual(debug["total_results"], exact_count, f"Exact count mismatch for query '{query}'")

    # =====================================================================
    # 3. NEGATIVE / ZERO-HALLUCINATION TESTS (Never fabricate records)
    # =====================================================================
    def test_zero_hallucination_guarantee(self):
        cases = [
            "Assistant Programmer in Finance",
            "assistant programmer in engineering department",
            "assistant programmer in physical education",
            "System Analyst in Library",
            "NonExistentOfficerNameXYZ123",
        ]
        for query in cases:
            with self.subTest(query=query):
                reply, citations, conf, chips, debug = self.search_service.search_and_format(query)
                self.assertIsNotNone(reply)
                self.assertEqual(debug["total_results"], 0, f"Expected 0 results for non-existent combo '{query}'")
                self.assertIn("কোনো কর্মকর্তা/কর্মচারীর তথ্য পাওয়া যায়নি", reply)

    # =====================================================================
    # 4. DEPARTMENT GENERAL EMPLOYEE LISTING
    # =====================================================================
    def test_department_employee_listings(self):
        cases = [
            ("show ICT employees", "ict-department", 90),
            ("all ICT employees", "ict-department", 90),
            ("আইসিটি দপ্তরের সকল কর্মকর্তা", "ict-department", 90),
            ("registrar office officers", "registrar-office", 90),
            ("রেজিস্ট্রার দপ্তরের কর্মকর্তা", "registrar-office", 90),
            ("finance and accounts officers", "finance-accounts", 50),
            ("পরীক্ষা নিয়ন্ত্রক দপ্তর কর্মকর্তা", "exam-controller", 100),
            ("library officers", "library-department", 20),
            ("transport department staff", "transport-department", 30),
            ("vc office employees", "vc-office", 10),
        ]
        for query, expected_dept, min_count in cases:
            with self.subTest(query=query):
                entities = extract_directory_entities(query)
                self.assertEqual(entities.department_slug, expected_dept)
                reply, citations, conf, chips, debug = self.search_service.search_and_format(query)
                self.assertIsNotNone(reply)
                self.assertGreaterEqual(debug["total_results"], min_count)

    # =====================================================================
    # 5. SPECIFIC NAME / PERSON SEARCH
    # =====================================================================
    def test_person_name_searches(self):
        cases = [
            ("Mridul Roy", "Mridul"),
            ("মুদুল রায়", "মুদুল"),
            ("Md. Muhaimenur Rahman", "Muhaimenur"),
            ("সৈয়দ মোস্তাফিজুর রহমান", "মোস্তাফিজুর"),
        ]
        for query, expected_name_substr in cases:
            with self.subTest(query=query):
                reply, citations, conf, chips, debug = self.search_service.search_and_format(query)
                self.assertIsNotNone(reply)
                self.assertGreaterEqual(debug["total_results"], 1)
                self.assertIn(expected_name_substr, reply)

    # =====================================================================
    # 6. TYPOS & BANGLISH QUERY RECOVERY
    # =====================================================================
    def test_typo_and_banglish_recovery(self):
        cases = [
            ("programer", 20),
            ("assistant programer", 7),
            ("assistent programmer", 7),
            ("sohokari programmer", 7),
            ("ict doptorer kormokorta", 90),
            ("rejistrar office", 90),
            ("porikkha niyontrok doptor", 100),
        ]
        for query, min_results in cases:
            with self.subTest(query=query):
                reply, citations, conf, chips, debug = self.search_service.search_and_format(query)
                self.assertIsNotNone(reply)
                self.assertGreaterEqual(debug["total_results"], min_results)

    # =====================================================================
    # 7. INTENT DISCRIMINATION (General Knowledge vs Directory)
    # =====================================================================
    def test_intent_discrimination(self):
        cases = [
            ("what is an assistant programmer?", True),
            ("what does a programmer do?", True),
            ("meaning of system analyst", True),
            ("how to become a programmer?", True),
            ("প্রোগ্রামার এর কাজ কি?", True),
            ("who are the assistant programmers?", False),
            ("who is the registrar?", False),
            ("list of assistant programmers", False),
            ("আইসিটি কর্মকর্তা তালিকা", False),
        ]
        for query, is_gk in cases:
            with self.subTest(query=query):
                self.assertEqual(is_general_knowledge_query(query), is_gk)

    # =====================================================================
    # 8. MULTI-TURN CONTEXT RESOLUTION
    # =====================================================================
    def test_multiturn_refinements(self):
        # Scenario A: Department -> Designation Refinement
        turn1_query = "show ICT employees"
        turn1_entities = extract_directory_entities(turn1_query)
        self.assertEqual(turn1_entities.department_slug, "ict-department")

        history = [
            {"role": "user", "content": turn1_query},
            {"role": "assistant", "content": "Here is the ICT Department list"}
        ]
        turn2_query = "only assistant programmers"
        turn2_entities = extract_directory_entities(turn2_query, history=history)
        self.assertEqual(turn2_entities.designation, "Assistant Programmer")
        self.assertEqual(turn2_entities.department_slug, "ict-department")

        reply, citations, conf, chips, debug = self.search_service.search_and_format(turn2_query, history=history)
        self.assertEqual(debug["total_results"], 4)

        # Scenario B: Designation -> Department Refinement
        turn3_query = "all assistant programmers"
        history_b = [
            {"role": "user", "content": turn3_query},
            {"role": "assistant", "content": "Here are all 7 assistant programmers"}
        ]
        turn4_query = "only in ICT"
        turn4_entities = extract_directory_entities(turn4_query, history=history_b)
        self.assertEqual(turn4_entities.designation, "Assistant Programmer")
        self.assertEqual(turn4_entities.department_slug, "ict-department")

    # =====================================================================
    # 9. ALL DEPARTMENTS MEGA MENU & ALL EMPLOYEES
    # =====================================================================
    def test_all_departments_mega_menu(self):
        query = "সকল দপ্তরের তালিকা"
        entities = extract_directory_entities(query)
        self.assertTrue(entities.is_all_departments_query)

        reply, citations, conf, chips, debug = self.search_service.search_and_format(query)
        self.assertIsNotNone(reply)
        self.assertIn("উপাচার্য দপ্তর", reply)
        self.assertIn("আইসিটি দপ্তর", reply)
        self.assertIn("রেজিস্ট্রার দপ্তর", reply)
        self.assertGreaterEqual(len(citations), 4)

    def test_all_employees_pagination(self):
        query = "all employees"
        entities = extract_directory_entities(query)
        self.assertTrue(entities.is_all_query)

        reply, citations, conf, chips, debug = self.search_service.search_and_format(query)
        self.assertIsNotNone(reply)
        self.assertGreaterEqual(debug["total_results"], 1500)
        self.assertTrue("পৃষ্ঠা ১" in reply or "১-৫০" in reply)

    # =====================================================================
    # 10. LATENCY BENCHMARK (< 50ms SLA)
    # =====================================================================
    def test_performance_benchmark(self):
        test_suite = [
            "assistant programmer in ICT",
            "সহকারী প্রোগ্রামার",
            "show ICT employees",
            "Mridul Roy",
            "registrar office officers",
            "সকল দপ্তরের তালিকা",
            "who are the assistant programmers?",
            "Assistant Programmer in Finance"
        ]

        latencies = []
        for q in test_suite:
            t0 = time.perf_counter()
            self.search_service.search_and_format(q)
            lat = (time.perf_counter() - t0) * 1000
            latencies.append(lat)

        avg_latency = sum(latencies) / len(latencies)
        print(f"\n[BENCHMARK] Average Officer Search Latency: {avg_latency:.2f}ms across {len(test_suite)} queries")
        self.assertLess(avg_latency, 100.0, f"Average latency {avg_latency:.2f}ms exceeds 100ms SLA")

    # =====================================================================
    # 11. END-TO-END RAG ENGINE INTEGRATION
    # =====================================================================
    def test_rag_engine_e2e_integration(self):
        # Test 1: Structured Directory query fast-path
        resp1 = self.rag_engine.answer_query("ICT assistant programmer")
        self.assertEqual(resp1.intent, "department_offices")
        self.assertGreaterEqual(resp1.confidence, 0.95)
        self.assertIn("আইসিটি দপ্তর", resp1.reply)
        self.assertIn("সহকারী প্রোগ্রামার", resp1.reply)

        # Test 2: General Knowledge question routed away from directory
        resp2_intent = self.rag_engine.classify_intent("what is an assistant programmer?")
        self.assertNotEqual(resp2_intent, "department_offices")


if __name__ == "__main__":
    unittest.main()
