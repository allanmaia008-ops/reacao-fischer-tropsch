import hashlib
from pathlib import Path
import sqlite3
import tempfile
import unittest

from plataforma_ltft.auth import AuthenticationError, AuthService
from plataforma_ltft.database import Database


class AuthServiceTests(unittest.TestCase):
    def setUp(self):
        self.tempdir = tempfile.TemporaryDirectory()
        self.database = Database(Path(self.tempdir.name) / "platform.sqlite3")
        self.database.migrate()
        self.auth = AuthService(self.database)
        self.admin_id = self.auth.bootstrap_admin("admin@example.org", "Admin-passphrase-2026")
        self.database.create_project("project-a", "Project A")
        self.database.create_project("project-b", "Project B")

    def tearDown(self):
        self.tempdir.cleanup()

    def test_password_hash_session_digest_and_revocation(self):
        user_id = self.auth.create_user(
            self.admin_id, "researcher", "Research-passphrase-2026", role="researcher"
        )
        token = self.auth.authenticate("RESEARCHER", "Research-passphrase-2026")
        self.assertEqual(self.auth.session_user(token)["user_id"], user_id)
        digest = hashlib.sha256(token.encode("utf-8")).hexdigest()
        with self.database.connection() as connection:
            row = connection.execute("SELECT token_sha256 FROM auth_sessions").fetchone()
            password_hash = connection.execute(
                "SELECT password_hash FROM users WHERE user_id=?", (user_id,)
            ).fetchone()[0]
        self.assertEqual(row["token_sha256"], digest)
        self.assertNotIn(token, row["token_sha256"])
        self.assertTrue(password_hash.startswith("scrypt$"))
        self.assertNotIn("Research-passphrase-2026", password_hash)
        self.assertTrue(self.auth.revoke_session(token))
        self.assertIsNone(self.auth.session_user(token))
        self.assertFalse(self.auth.revoke_session(token))

    def test_project_roles_and_global_role_apply_least_privilege(self):
        researcher_id = self.auth.create_user(
            self.admin_id, "researcher", "Research-passphrase-2026", role="researcher"
        )
        viewer_id = self.auth.create_user(
            self.admin_id, "viewer", "Viewer-passphrase-2026", role="viewer"
        )
        self.auth.set_project_membership(self.admin_id, researcher_id, "project-a", role="researcher")
        self.auth.set_project_membership(self.admin_id, researcher_id, "project-b", role="viewer")
        self.auth.set_project_membership(self.admin_id, viewer_id, "project-a", role="researcher")
        researcher_token = self.auth.authenticate("researcher", "Research-passphrase-2026")
        viewer_token = self.auth.authenticate("viewer", "Viewer-passphrase-2026")
        self.assertTrue(self.auth.authorize(researcher_token, "dft.write", project_id="project-a"))
        self.assertFalse(self.auth.authorize(researcher_token, "dft.write", project_id="project-b"))
        self.assertTrue(self.auth.authorize(researcher_token, "dft.read", project_id="project-b"))
        self.assertFalse(self.auth.authorize(viewer_token, "dft.write", project_id="project-a"))
        self.assertTrue(self.auth.authorize(viewer_token, "dft.read", project_id="project-a"))
        self.assertFalse(self.auth.authorize(researcher_token, "dft.read", project_id="unknown-project"))
        self.assertFalse(self.auth.authorize("invalid", "dft.read", project_id="project-a"))

    def test_bootstrap_admin_is_one_time_and_admin_required_for_user_creation(self):
        with self.assertRaises(AuthenticationError):
            self.auth.bootstrap_admin("another-admin", "Another-passphrase-2026")
        researcher_id = self.auth.create_user(
            self.admin_id, "researcher", "Research-passphrase-2026", role="researcher"
        )
        with self.assertRaises(AuthenticationError):
            self.auth.create_user(researcher_id, "other-user", "Other-passphrase-2026", role="viewer")
        with self.assertRaises(AuthenticationError):
            self.auth.authenticate("researcher", "wrong-password-value")

    def test_credentials_roles_and_session_lifetime_are_validated(self):
        with self.assertRaises(ValueError):
            self.auth.create_user(self.admin_id, "ab", "Research-passphrase-2026", role="viewer")
        with self.assertRaises(ValueError):
            self.auth.create_user(self.admin_id, "new-user", "short", role="viewer")
        with self.assertRaises(ValueError):
            self.auth.create_user(self.admin_id, "new-user", "Long-enough-passphrase", role="owner")
        with self.assertRaises(ValueError):
            AuthService(self.database, session_hours=25)


if __name__ == "__main__":
    unittest.main()
