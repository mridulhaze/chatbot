import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.agents.scraped_data_analyzer import ScrapedDataAnalyzerAgent
from backend.agents.knowledge_enricher import KnowledgeEnricherAgent
from backend.agents.knowledge_provenance import KnowledgeProvenanceAgent
from backend.agents.autonomous_24x7_worker import Autonomous24x7Worker
from mcp_servers.enrichment_mcp.server import EnrichmentMCPServer

class TestAutonomous24x7Enrichment(unittest.TestCase):
    def setUp(self):
        self.analyzer = ScrapedDataAnalyzerAgent()
        self.enricher = KnowledgeEnricherAgent()
        self.provenance = KnowledgeProvenanceAgent()
        self.worker = Autonomous24x7Worker(interval_seconds=600)
        self.mcp_server = EnrichmentMCPServer()

    def test_01_analyze_scraped_page(self):
        sample_page = {
            "id": 9999,
            "url": "https://www.nu.ac.bd/notice-2026-honours-exam.php",
            "title": "২০২৪-২০২৫ শিক্ষাবর্ষের অনার্স ১ম বর্ষ পরীক্ষার সংশোধিত সময়সূচি",
            "section": "EXAMINATION",
            "published_date": "2026-08-15",
            "content_text": "জাতীয় বিশ্ববিদ্যালয়ের ২০২৪-২০২৫ শিক্ষাবর্ষের অনার্স ১ম বর্ষ পরীক্ষার সংশোধিত সময়সূচি প্রকাশিত হয়েছে। পরীক্ষা শুরু হবে ১৫ সেপ্টেম্বর ২০২৬ থেকে প্রতিদিন দুপুর ১:৩০ টায়। প্রবেশপত্র ও রেজিস্ট্রেশন কার্ড সঙ্গে আনতে হবে।"
        }
        res = self.analyzer.analyze_page(sample_page)
        self.assertIn("summary_bn", res)
        self.assertIn("qa_pairs", res)
        self.assertTrue(len(res["qa_pairs"]) >= 1)
        self.assertIn("question_bn", res["qa_pairs"][0])

    def test_02_enrich_knowledge_ingestion(self):
        sample_analysis = {
            "url": "https://www.nu.ac.bd/notice-test.php",
            "title": "Test Circular for 24/7 Enrichment",
            "section": "ADMISSION",
            "summary_bn": "ভর্তি পরীক্ষার টেস্ট সার্কুলার।",
            "key_facts": ["যোগ্যতা: জিপিএ ৩.০০", "আবেদনের শেষ তারিখ: ৩০ আগস্ট ২০২৬"],
            "qa_pairs": [
                {
                    "question_bn": "টেস্ট ভর্তি আবেদনের শেষ তারিখ কবে?",
                    "answer_bn": "৩০ আগস্ট ২০২৬ পর্যন্ত অনলাইনে আবেদন করা যাবে।",
                    "question_en": "When is the test admission deadline?",
                    "answer_en": "Online applications are accepted till 30 August 2026."
                }
            ],
            "analyzed_by": "TestEnrichmentRunner"
        }
        res = self.enricher.enrich_knowledge(sample_analysis)
        self.assertEqual(res["qa_synthesized"], 1)
        self.assertTrue(res["log_id"] > 0)

    def test_03_record_provenance_and_manifest(self):
        sample_record = {
            "url": "https://www.nu.ac.bd/manifest-test.php",
            "title": "Manifest Test Notice",
            "section": "GENERAL",
            "summary_bn": "ম্যানিফেস্ট টেস্ট বিজ্ঞপ্তি।",
            "qa_pairs": [{"question_bn": "প্রশ্ন", "answer_bn": "উত্তর"}],
            "key_facts": ["ফ্যাক্ট ১"]
        }
        entry = self.provenance.record_update(sample_record)
        self.assertIn("update_id", entry)
        
        manifest = self.provenance.get_manifest()
        self.assertIn("manifest_version", manifest)
        self.assertIn("statistics", manifest)
        self.assertTrue(manifest["statistics"]["total_enrichment_cycles"] >= 1)

    def test_04_mcp_enrichment_tools(self):
        status_res = self.mcp_server.get_enrichment_status()
        self.assertTrue(status_res["success"])
        self.assertIn("is_running", status_res["data"])

        updates_res = self.mcp_server.get_recent_knowledge_updates(limit=5)
        self.assertTrue(updates_res["success"])
        self.assertIsInstance(updates_res["data"], list)

        manifest_res = self.mcp_server.get_knowledge_manifest()
        self.assertTrue(manifest_res["success"])
        self.assertEqual(manifest_res["data"]["manifest_version"], "2.0.0")

if __name__ == "__main__":
    unittest.main()
