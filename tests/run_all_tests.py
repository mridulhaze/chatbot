import unittest
import sys
from pathlib import Path

# Add project root to sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from backend.services.token_service import TokenDomainService, get_token_domain_service
from backend.models.schemas import TokenCreateRequest
from mcp_servers.token_mcp.server import get_token_mcp_server
from mcp_servers.knowledge_mcp.server import get_knowledge_mcp_server
from mcp_servers.document_mcp.server import get_document_mcp_server
from backend.orchestrator.intent import get_intent_classifier
from backend.orchestrator.router import get_skill_router
from backend.orchestrator.skill_registry import get_skill_registry
from backend.orchestrator.mcp_client import get_mcp_client
from backend.core.security import hash_password, verify_password, create_jwt_token, decode_jwt_token, encrypt_credential_data, decrypt_credential_data
from backend.services.credential_service import get_credential_service
from mcp_servers.credential_mcp.server import get_credential_mcp_server

class TestNUAIAssistantPlatform(unittest.TestCase):
    
    def test_atomic_sequence_generation(self):
        service = get_token_domain_service()
        token_id1 = service.generate_atomic_token_id()
        token_id2 = service.generate_atomic_token_id()
        self.assertTrue(token_id1.startswith("NU-"))
        self.assertTrue(token_id2.startswith("NU-"))
        self.assertNotEqual(token_id1, token_id2)

    def test_token_creation_and_public_status(self):
        service = get_token_domain_service()
        req = TokenCreateRequest(
            service_code="EMS",
            problem="Cannot login to EMS student dashboard",
            user_name="Rahim Uddin",
            user_phone="01700000000",
            registration_no="1920000000",
            priority="NORMAL"
        )
        res = service.create_token(req)
        self.assertTrue(res.success)
        self.assertTrue(res.token_id.startswith("NU-"))
        self.assertEqual(res.status, "PENDING")

        public_status = service.get_public_token_status(res.token_id)
        self.assertIsNotNone(public_status)
        self.assertEqual(public_status.token_id, res.token_id)
        self.assertEqual(public_status.status, "PENDING")

    def test_status_transitions_and_rules(self):
        service = get_token_domain_service()
        req = TokenCreateRequest(service_code="TC", problem="College transfer processing delay")
        res = service.create_token(req)
        t_id = res.token_id

        # PENDING -> ASSIGNED
        ok, msg = service.update_status(t_id, "ASSIGNED", changed_by="ADMIN")
        self.assertTrue(ok)

        # ASSIGNED -> PROCESSING
        ok, msg = service.update_status(t_id, "PROCESSING", changed_by="SOLVER")
        self.assertTrue(ok)

        # PROCESSING -> SOLVED
        ok, msg = service.solve_token(t_id, "TC application synchronized and approved.", solver_name="Registration Desk")
        self.assertTrue(ok)

        # SOLVED -> CLOSED
        ok, msg = service.update_status(t_id, "CLOSED", changed_by="ADMIN")
        self.assertTrue(ok)

        # Illegal: CLOSED -> PENDING
        ok, msg = service.update_status(t_id, "PENDING", changed_by="USER")
        self.assertFalse(ok)

    def test_token_mcp_server_tools(self):
        token_mcp = get_token_mcp_server()
        res = token_mcp.get_services()
        self.assertTrue(res["success"])
        self.assertIsInstance(res["data"], list)
        self.assertTrue(len(res["data"]) > 0)
        self.assertTrue(any(s["service_code"] == "EMS" for s in res["data"]))

        create_res = token_mcp.create_token(
            service_code="CERTIFICATE",
            problem="Certificate delivery status inquiry",
            user_name="Karim Khan"
        )
        self.assertTrue(create_res["success"])
        t_id = create_res["data"]["token_id"]

        status_res = token_mcp.get_token_status(token_id=t_id)
        self.assertTrue(status_res["success"])
        self.assertEqual(status_res["data"]["token_id"], t_id)
        self.assertEqual(status_res["data"]["status"], "PENDING")

    def test_knowledge_and_document_mcp_servers(self):
        kmcp = get_knowledge_mcp_server()
        res = kmcp.search_notice(query="examination", limit=2)
        self.assertTrue(res["success"])

        dmcp = get_document_mcp_server()
        d_res = dmcp.search_documents(query="form", limit=2)
        self.assertTrue(d_res["success"])

    def test_skill_registry_and_routing(self):
        registry = get_skill_registry()
        skills = registry.list_skills()
        self.assertIn("token_service", skills)
        self.assertIn("nu_general", skills)
        self.assertIn("examination", skills)
        self.assertIn("admission", skills)
        self.assertIn("service_credentials", skills)

        classifier = get_intent_classifier()
        intent, entities = classifier.classify("Check status of NU-2026-000123")
        self.assertEqual(intent, "TOKEN_STATUS")
        self.assertEqual(entities.get("token_id"), "NU-2026-000123")

        router = get_skill_router()
        self.assertEqual(router.route("TOKEN_STATUS", {"token_id": "NU-2026-000123"}), "token_service")
        self.assertEqual(router.route("EXAM_QUERY", {}), "examination")
        self.assertEqual(router.route("GENERAL_NU_QUERY", {}), "nu_general")

    def test_security_and_jwt(self):
        pwd = "test_secret_password"
        hashed = hash_password(pwd)
        self.assertTrue(verify_password(pwd, hashed))
        self.assertFalse(verify_password("wrong", hashed))

        payload = {"user_id": 99, "username": "admin_user", "role": "ADMIN"}
        token = create_jwt_token(payload)
        decoded = decode_jwt_token(token)
        self.assertIsNotNone(decoded)
        self.assertEqual(decoded["username"], "admin_user")
        self.assertEqual(decoded["role"], "ADMIN")

    def test_aes_gcm_credential_encryption(self):
        plain = "NuStudentSecret2026#!"
        cipher = encrypt_credential_data(plain)
        self.assertNotEqual(plain, cipher)
        self.assertNotIn(plain, cipher)

        decrypted = decrypt_credential_data(cipher)
        self.assertEqual(decrypted, plain)

        # Tampering protection test
        tampered = cipher[:-4] + "AAAA"
        self.assertIsNone(decrypt_credential_data(tampered))

    def test_credential_service_and_mcp_server(self):
        cred_service = get_credential_service()
        user_id = "test_student_123"

        # 1. Dynamic fields
        fields = cred_service.get_service_fields("EMS")
        self.assertTrue(len(fields) >= 2)
        self.assertTrue(any(f["field_name"] == "username" for f in fields))
        self.assertTrue(any(f["field_name"] == "password" for f in fields))

        # 2. Save credentials
        ok, msg, cred_id = cred_service.save_credential(
            user_id=user_id,
            service_code="EMS",
            username="student_ems_007",
            password="SecureEmsPassword123"
        )
        self.assertTrue(ok)
        self.assertIsNotNone(cred_id)

        # 3. Status check (password must NOT be in output)
        status_data = cred_service.get_credential_status(user_id, "EMS")
        self.assertTrue(status_data["configured"])
        self.assertEqual(status_data["username"], "student_ems_007")
        self.assertNotIn("password", status_data)

        # 4. Verification test
        v_ok, v_msg = cred_service.verify_credential(user_id, "EMS")
        self.assertTrue(v_ok)

        # 5. MCP Server wrapper test
        cred_mcp = get_credential_mcp_server()
        mcp_res = cred_mcp.get_user_services(user_id)
        self.assertTrue(mcp_res["success"])
        self.assertIsInstance(mcp_res["data"], list)
        ems_item = next(item for item in mcp_res["data"] if item["service_code"] == "EMS")
        self.assertTrue(ems_item["is_configured"])
        self.assertEqual(ems_item["credential_status"], "ACTIVE")

        # 6. Delete test
        del_ok, del_msg = cred_service.delete_credential(user_id, "EMS")
        self.assertTrue(del_ok)
        del_status = cred_service.get_credential_status(user_id, "EMS")
        self.assertFalse(del_status["configured"])

    def test_24x7_autonomous_enrichment_agents(self):
        from backend.agents.scraped_data_analyzer import ScrapedDataAnalyzerAgent
        from backend.agents.knowledge_provenance import KnowledgeProvenanceAgent
        from mcp_servers.enrichment_mcp.server import get_enrichment_mcp_server

        analyzer = ScrapedDataAnalyzerAgent()
        provenance = KnowledgeProvenanceAgent()
        enrich_mcp = get_enrichment_mcp_server()

        # 1. Analyze page
        sample_page = {
            "id": 8888,
            "url": "https://www.nu.ac.bd/notice-test-exam.php",
            "title": "ডিগ্রি পাস ও সার্টিফিকেট কোর্স পরীক্ষার বিজ্ঞপ্তি",
            "section": "EXAMINATION",
            "published_date": "2026-08-20",
            "content_text": "জাতীয় বিশ্ববিদ্যালয়ের ডিগ্রি পাস ও সার্টিফিকেট কোর্স পরীক্ষার সংশোধিত সময়সূচি প্রকাশ করা হলো।"
        }
        analysis = analyzer.analyze_page(sample_page)
        self.assertIn("summary_bn", analysis)
        self.assertTrue(len(analysis.get("qa_pairs", [])) >= 1)

        # 2. Record provenance & manifest
        entry = provenance.record_update(analysis)
        self.assertIn("update_id", entry)
        manifest = provenance.get_manifest()
        self.assertEqual(manifest.get("manifest_version"), "2.0.0")

        # 3. MCP tool check
        res = enrich_mcp.get_enrichment_status()
        self.assertTrue(res["success"])
        self.assertIn("is_running", res["data"])

from tests.test_officer_search import TestOfficerSearchEngine
from tests.test_result_search import TestResultSearchEngine

if __name__ == "__main__":
    unittest.main()
