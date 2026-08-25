"""
Test Suite for Activity Tracker, System Audit Logs, and Report Exporters (PDF & Excel)
"""

import sys
import unittest
from pathlib import Path

BASE_DIR = Path("E:/projects/AI_CHAT_BOT")
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from backend.services.activity_tracker import ActivityTracker, get_activity_tracker
from backend.services.report_exporter import ReportExporter, get_report_exporter

class TestActivityLogsAndExports(unittest.TestCase):
    def setUp(self):
        self.tracker = get_activity_tracker()
        self.exporter = get_report_exporter()

    def test_01_record_activity_events(self):
        """Test recording various system activity events."""
        self.tracker.record_event(
            event_type="SERVICE_PROVIDED",
            service_code="EMS",
            user_identifier="REG_2026_9999",
            solver_name="ICT Support",
            status="SUCCESS",
            details="Tested EMS password recovery guidance"
        )
        self.tracker.record_event(
            event_type="BARCODE_GENERATED",
            service_code="MOBILE_QR",
            user_identifier="STUDENT_MOBILE_APP",
            status="SUCCESS",
            details="Generated mobile QR camera link"
        )

        records = self.tracker.get_activity_records(limit=10)
        self.assertIsInstance(records, list)
        self.assertGreaterEqual(len(records), 2)

    def test_02_summary_metrics(self):
        """Test fetching aggregated KPI metric counters."""
        summary = self.tracker.get_summary_metrics()
        self.assertIn("total_services_provided", summary)
        self.assertIn("total_barcodes_generated", summary)
        self.assertIn("total_tokens", summary)
        self.assertIn("total_solved", summary)
        self.assertIn("total_pending", summary)
        self.assertIn("service_breakdown", summary)
        self.assertGreaterEqual(summary["total_services_provided"], 1)

    def test_03_generate_excel_report(self):
        """Test generating formatted multi-sheet Excel spreadsheet."""
        excel_bytes = self.exporter.generate_excel_report()
        self.assertIsInstance(excel_bytes, bytes)
        self.assertGreater(len(excel_bytes), 1000)
        # Verify valid PK zip header for xlsx
        self.assertTrue(excel_bytes.startswith(b"PK"))

    def test_04_generate_pdf_report(self):
        """Test generating executive PDF audit report."""
        pdf_bytes = self.exporter.generate_pdf_report()
        self.assertIsInstance(pdf_bytes, bytes)
        self.assertGreater(len(pdf_bytes), 1000)
        # Verify valid PDF header
        self.assertTrue(pdf_bytes.startswith(b"%PDF"))

if __name__ == "__main__":
    unittest.main()
