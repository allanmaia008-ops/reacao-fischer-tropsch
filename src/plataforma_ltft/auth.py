"""Minimal, project-scoped authentication and authorization primitives (FT-042).

This service is not yet connected to Streamlit/API middleware. Production use
still requires HTTPS, rate limiting, CSRF protection, account recovery, and an
institutional identity provider review.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
import hashlib
import hmac
import re
import secrets
import sqlite3
import uuid

from .database import Database, _utc_now

AUTH_ROLES = {"admin", "researcher", "viewer"}
PROJECT_ROLES = {"researcher", "viewer"}
RESEARCHER_PERMISSIONS = {
    "project.read", "project.write", "run.read", "run.write",
    "evidence.read", "evidence.write", "dft.read", "dft.write",
}
VIEWER_PERMISSIONS = {"project.read", "run.read", "evidence.read", "dft.read"}
ALL_PERMISSIONS = RESEARCHER_PERMISSIONS | VIEWER_PERMISSIONS | {"user.manage"}
_USERNAME = re.compile(r"^[A-Za-z0-9_.@-]{3,100}$")
_DUMMY_SALT = bytes.fromhex("4c54465461757468646f6e6f746573")
_DUMMY_DIGEST = hashlib.scrypt(b"not-a-real-password", salt=_DUMMY_SALT, n=2**14, r=8, p=1, dklen=32)


class AuthenticationError(ValueError):
    """Raised when authentication or authorization is denied."""


def _hash_password(password: str, *, salt: bytes | None = None) -> str:
    salt = salt or secrets.token_bytes(16)
    digest = hashlib.scrypt(password.encode("utf-8"), salt=salt, n=2**14, r=8, p=1, dklen=32)
    return "scrypt$16384$8$1$" + salt.hex() + "$" + digest.hex()


def _verify_password(password: str, encoded: str) -> bool:
    try:
        algorithm, n, r, p, salt_hex, expected_hex = encoded.split("$")
        if algorithm != "scrypt":
            return False
        actual = hashlib.scrypt(
            password.encode("utf-8"),
            salt=bytes.fromhex(salt_hex),
            n=int(n),
            r=int(r),
            p=int(p),
            dklen=len(bytes.fromhex(expected_hex)),
        )
        return hmac.compare_digest(actual.hex(), expected_hex)
    except (ValueError, TypeError):
        return False


class AuthService:
    """Password/session service with explicit global and project-scoped roles."""

    def __init__(self, database: Database, *, session_hours: int = 8):
        if session_hours <= 0 or session_hours > 24:
            raise ValueError("session_hours must be between 1 and 24")
        self.database = database
        self.session_hours = session_hours

    def bootstrap_admin(self, username: str, password: str) -> str:
        """Create the first administrator only; subsequent calls are forbidden."""
        self._validate_credentials(username, password)
        with self.database.connection() as connection:
            connection.execute("BEGIN IMMEDIATE")
            try:
                count = connection.execute("SELECT COUNT(*) FROM users").fetchone()[0]
                if count:
                    raise AuthenticationError("initial administrator already exists")
                user_id = str(uuid.uuid4())
                connection.execute(
                    "INSERT INTO users(user_id, username, password_hash, is_active, created_at) VALUES (?, ?, ?, 1, ?)",
                    (user_id, username.strip().lower(), _hash_password(password), _utc_now()),
                )
                connection.execute("INSERT INTO user_roles(user_id, role) VALUES (?, 'admin')", (user_id,))
                self.database._append_event(connection, None, user_id, "auth.admin_bootstrapped", {"user_id":user_id,"role":"admin"}, _utc_now())
                connection.commit()
            except Exception:
                connection.rollback()
                raise
        return user_id

    def create_user(self, actor_user_id: str, username: str, password: str, *, role: str) -> str:
        """Create an account; only an active global administrator may do so."""
        self._validate_credentials(username, password)
        if role not in AUTH_ROLES:
            raise ValueError(f"unsupported global role: {role}")
        self._require_global_admin(actor_user_id)
        user_id = str(uuid.uuid4())
        try:
            with self.database.connection() as connection:
                connection.execute(
                    "INSERT INTO users(user_id, username, password_hash, is_active, created_at) VALUES (?, ?, ?, 1, ?)",
                    (user_id, username.strip().lower(), _hash_password(password), _utc_now()),
                )
                connection.execute("INSERT INTO user_roles(user_id, role) VALUES (?, ?)", (user_id, role))
                self.database._append_event(connection, None, actor_user_id, "auth.user_created", {"user_id":user_id,"role":role}, _utc_now())
        except sqlite3.IntegrityError as exc:
            raise AuthenticationError("username already exists or account violates database constraints") from exc
        return user_id

    def set_project_membership(
        self,
        actor_user_id: str,
        user_id: str,
        project_id: str,
        *,
        role: str,
    ) -> None:
        self._require_global_admin(actor_user_id)
        if role not in PROJECT_ROLES:
            raise ValueError(f"unsupported project role: {role}")
        with self.database.connection() as connection:
            connection.execute(
                "INSERT INTO project_memberships(user_id, project_id, role) VALUES (?, ?, ?) "
                "ON CONFLICT(user_id, project_id) DO UPDATE SET role=excluded.role",
                (user_id, project_id, role),
            )
            self.database._append_event(connection, project_id, actor_user_id, "auth.project_membership_changed", {"user_id":user_id,"role":role}, _utc_now())

    def authenticate(self, username: str, password: str) -> str:
        """Return a one-time bearer token; only its SHA-256 digest is persisted."""
        normalized = username.strip().lower()
        with self.database.connection() as connection:
            row = connection.execute(
                "SELECT u.user_id, u.password_hash, u.is_active FROM users u "
                "WHERE u.username=? COLLATE NOCASE",
                (normalized,),
            ).fetchone()
        stored_hash = row["password_hash"] if row else (
            "scrypt$16384$8$1$" + _DUMMY_SALT.hex() + "$" + _DUMMY_DIGEST.hex()
        )
        valid = _verify_password(password, stored_hash)
        if row is None or not row["is_active"] or not valid:
            raise AuthenticationError("invalid credentials or inactive account")

        token = secrets.token_urlsafe(32)
        now = datetime.now(timezone.utc)
        expires = (now + timedelta(hours=self.session_hours)).isoformat(timespec="seconds").replace("+00:00", "Z")
        digest = hashlib.sha256(token.encode("utf-8")).hexdigest()
        with self.database.connection() as connection:
            connection.execute(
                "INSERT INTO auth_sessions(token_sha256, user_id, created_at, expires_at) VALUES (?, ?, ?, ?)",
                (digest, row["user_id"], now.isoformat(timespec="seconds").replace("+00:00", "Z"), expires),
            )
            self.database._append_event(connection, None, row["user_id"], "auth.session_created", {"user_id":row["user_id"],"expires_at":expires}, now.isoformat(timespec="seconds").replace("+00:00", "Z"))
        return token

    def session_user(self, token: str) -> dict[str, str] | None:
        if not token:
            return None
        digest = hashlib.sha256(token.encode("utf-8")).hexdigest()
        now = datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")
        with self.database.connection() as connection:
            row = connection.execute(
                "SELECT u.user_id, u.username, r.role FROM auth_sessions s "
                "JOIN users u ON u.user_id=s.user_id JOIN user_roles r ON r.user_id=u.user_id "
                "WHERE s.token_sha256=? AND s.revoked_at IS NULL AND s.expires_at>? AND u.is_active=1",
                (digest, now),
            ).fetchone()
        if row is None:
            return None
        return {"user_id": row["user_id"], "username": row["username"], "role": row["role"]}

    def revoke_session(self, token: str) -> bool:
        digest = hashlib.sha256(token.encode("utf-8")).hexdigest()
        with self.database.connection() as connection:
            row = connection.execute("SELECT user_id FROM auth_sessions WHERE token_sha256=?", (digest,)).fetchone()
            cursor = connection.execute(
                "UPDATE auth_sessions SET revoked_at=? WHERE token_sha256=? AND revoked_at IS NULL",
                (_utc_now(), digest),
            )
            revoked = cursor.rowcount == 1
            if revoked and row:
                self.database._append_event(connection, None, row["user_id"], "auth.session_revoked", {"user_id":row["user_id"]}, _utc_now())
        return revoked

    def authorize(self, token: str, permission: str, *, project_id: str | None) -> bool:
        if permission not in ALL_PERMISSIONS:
            return False
        principal = self.session_user(token)
        if principal is None:
            return False
        if principal["role"] == "admin":
            return permission in ALL_PERMISSIONS
        if project_id is None:
            return False
        with self.database.connection() as connection:
            row = connection.execute(
                "SELECT role FROM project_memberships WHERE user_id=? AND project_id=?",
                (principal["user_id"], project_id),
            ).fetchone()
        if row is None:
            return False
        if principal["role"] == "viewer":
            allowed = VIEWER_PERMISSIONS
        else:
            allowed = RESEARCHER_PERMISSIONS if row["role"] == "researcher" else VIEWER_PERMISSIONS
        return permission in allowed

    def _require_global_admin(self, user_id: str) -> None:
        with self.database.connection() as connection:
            row = connection.execute(
                "SELECT u.is_active, r.role FROM users u JOIN user_roles r ON r.user_id=u.user_id "
                "WHERE u.user_id=?",
                (user_id,),
            ).fetchone()
        if row is None or not row["is_active"] or row["role"] != "admin":
            raise AuthenticationError("active administrator role required")

    @staticmethod
    def _validate_credentials(username: str, password: str) -> None:
        if not _USERNAME.fullmatch(username.strip()):
            raise ValueError("username must be 3-100 characters using letters, digits, ., _, @ or -")
        if len(password) < 12 or len(password) > 1024:
            raise ValueError("password must contain between 12 and 1024 characters")
