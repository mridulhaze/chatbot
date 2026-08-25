import unittest
import sys
import os
sys.path.insert(0, ".")

from token_service.service import get_token_service
from token_service.db import get_token_db_connection
from token_service.models import TokenCreateRequest
from backend.services.backup_service import get_backup_service

class TestBackupAndDelete(unittest.TestCase):
    def setUp(self):
        self.token_svc = get_token_service()
        self.backup_svc = get_backup_service()

    def test_01_backup_creation_and_listing(self):
        backup_path, meta = self.backup_svc.create_backup()
        self.assertTrue(backup_path.exists())
        self.assertIn("checksums", meta)
        self.assertIn("stats", meta)
        self.assertGreaterEqual(meta["stats"]["tokens_count"], 1)

        backups = self.backup_svc.list_backups()
        self.assertGreaterEqual(len(backups), 1)
        self.assertEqual(backups[0]["filename"], backup_path.name)
        print(f"[TEST 1 PASS] Backup created successfully: {backup_path.name} (Tokens: {meta['stats']['tokens_count']})")

    def test_02_token_soft_delete_and_restore_cycle(self):
        # 1. Create a test token
        req = TokenCreateRequest(
            problem="Test problem for delete and restore validation",
            service_type="OTHER",
            user_name="Test Student",
            user_phone="01700000000"
        )
        created = self.token_svc.create_token(req)
        t_id = created.token_id
        self.assertTrue(t_id.startswith("NU-"))

        # 2. Check token exists in active list
        active_tokens, total = self.token_svc.repo.list_tokens(search=t_id, role="SUPER_ADMIN")
        self.assertEqual(total, 1)

        # 3. Super Admin soft-deletes token
        del_success = self.token_svc.repo.soft_delete_token(t_id, admin_user="SuperAdmin")
        self.assertTrue(del_success)

        # 4. Token must NOT appear in standard active list
        active_after_del, total_after = self.token_svc.repo.list_tokens(search=t_id, role="SUPER_ADMIN")
        self.assertEqual(total_after, 0)

        # 5. Token must NOT appear in Solver view
        solver_tokens, s_total = self.token_svc.repo.list_tokens(search=t_id, role="SOLVER", department="ICT Support Team")
        self.assertEqual(s_total, 0)

        # 6. Token MUST appear in Trash / Deleted list
        trash_tokens, trash_total = self.token_svc.repo.list_tokens(status="DELETED", search=t_id, role="SUPER_ADMIN")
        self.assertEqual(trash_total, 1)
        self.assertEqual(trash_tokens[0]["token_id"], t_id)
        self.assertEqual(trash_tokens[0]["is_deleted"], 1)

        # 7. Super Admin restores token
        restore_success = self.token_svc.repo.restore_token(t_id, admin_user="SuperAdmin")
        self.assertTrue(restore_success)

        # 8. Token reappears in active list
        active_restored, rest_total = self.token_svc.repo.list_tokens(search=t_id, role="SUPER_ADMIN")
        self.assertEqual(rest_total, 1)
        self.assertEqual(active_restored[0]["token_id"], t_id)
        self.assertEqual(active_restored[0]["is_deleted"], 0)

        print(f"[TEST 2 PASS] Token {t_id} successfully cycled: Active -> Deleted -> Trash Verified -> Restored -> Active Verified.")

    def test_03_backup_restore_roundtrip(self):
        # 1. Create a backup
        backup_path, meta = self.backup_svc.create_backup()
        with open(backup_path, "rb") as f:
            zip_bytes = f.read()

        # 2. Perform restore from bytes
        res = self.backup_svc.restore_backup(zip_bytes, filename=backup_path.name)
        self.assertTrue(res["success"])
        self.assertIn("current_stats", res)
        print(f"[TEST 3 PASS] System restore roundtrip executed safely. Stats: {res['current_stats']}")

if __name__ == "__main__":
    unittest.main()
