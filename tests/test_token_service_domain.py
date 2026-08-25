import sys
import unittest
sys.path.insert(0, ".")
from backend.services.token_service import TokenDomainService, get_token_domain_service
from backend.models.schemas import TokenCreateRequest

class TestTokenServiceDomain(unittest.TestCase):
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

        # Verify public status protects PII
        public_status = service.get_public_token_status(res.token_id)
        self.assertIsNotNone(public_status)
        self.assertEqual(public_status.token_id, res.token_id)
        self.assertEqual(public_status.status, "PENDING")
        self.assertTrue(not hasattr(public_status, "user_phone") or getattr(public_status, "user_phone", None) is None)

    def test_status_transitions_and_rules(self):
        service = get_token_domain_service()
        req = TokenCreateRequest(service_code="TC", problem="College transfer processing delay")
        res = service.create_token(req)
        t_id = res.token_id

        # 1. PENDING -> ASSIGNED
        ok, msg = service.update_status(t_id, "ASSIGNED", changed_by="ADMIN")
        self.assertTrue(ok)

        # 2. ASSIGNED -> PROCESSING
        ok, msg = service.update_status(t_id, "PROCESSING", changed_by="SOLVER")
        self.assertTrue(ok)

        # 3. PROCESSING -> SOLVED
        ok, msg = service.solve_token(t_id, "TC application synchronized and approved.", solver_name="Registration Desk")
        self.assertTrue(ok)

        # 4. SOLVED -> CLOSED
        ok, msg = service.update_status(t_id, "CLOSED", changed_by="ADMIN")
        self.assertTrue(ok)

        # 5. Illegal transition: CLOSED -> PENDING should fail
        ok, msg = service.update_status(t_id, "PENDING", changed_by="USER")
        self.assertFalse(ok)

    def test_return_to_admin_flow(self):
        service = get_token_domain_service()
        req = TokenCreateRequest(
            service_code="EMS",
            problem="Special approval required for attendance deficiency.",
            user_name="Student Test",
            user_phone="01711000000"
        )
        created = service.create_token(req)
        t_id = created.token_id

        # Assign to solver
        ok, _ = service.assign_solver(t_id, solver_id=1, changed_by="ADMIN")
        self.assertTrue(ok)

        # Solver sends back to admin for further instructions
        ok, msg = service.return_to_admin(
            token_id=t_id,
            reason="Requires Vice-Chancellor special approval before processing.",
            solver_name="ICT Desk",
            changed_by="solver_ict"
        )
        self.assertTrue(ok)

        detail = service.get_admin_token_detail(t_id)
        self.assertEqual(detail.status, "PENDING")
        self.assertIn("Requires Vice-Chancellor special approval", detail.admin_note)

if __name__ == "__main__":
    unittest.main()

