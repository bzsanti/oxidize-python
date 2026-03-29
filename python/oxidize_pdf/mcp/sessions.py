"""Session lifecycle management for stateful PDF creation."""

import threading
import time

__all__ = ["SessionStore", "SessionLimitError"]
from typing import Any
from uuid import uuid4


class SessionLimitError(RuntimeError):
    """Raised when the session store is at maximum capacity."""


class SessionStore:
    """Thread-safe in-memory session store with auto-expiry and optional capacity limit."""

    def __init__(
        self,
        max_age_seconds: float = 3600,
        max_sessions: int = 0,
    ) -> None:
        self._sessions: dict[str, dict[str, Any]] = {}
        self._timestamps: dict[str, float] = {}
        self._max_age = max_age_seconds
        self._max_sessions = max_sessions  # 0 = unlimited
        self._lock = threading.Lock()

    def create(self, data: dict[str, Any]) -> str:
        """Create a new session and return its UUID.

        Auto-purges expired sessions before checking the capacity limit.
        Raises SessionLimitError if at capacity after purging.
        """
        with self._lock:
            self._purge_expired_unlocked()
            if self._max_sessions > 0 and len(self._sessions) >= self._max_sessions:
                raise SessionLimitError(
                    f"Session limit reached ({self._max_sessions}). "
                    "Delete existing sessions to create new ones."
                )
            session_id = str(uuid4())
            self._sessions[session_id] = data
            self._timestamps[session_id] = time.monotonic()
            return session_id

    def get(self, session_id: str) -> dict[str, Any] | None:
        """Retrieve session data, or None if not found or expired."""
        with self._lock:
            if session_id not in self._sessions:
                return None
            ts = self._timestamps.get(session_id, 0.0)
            if (time.monotonic() - ts) > self._max_age:
                self._delete_unlocked(session_id)
                return None
            return self._sessions[session_id]

    def update(self, session_id: str, data: dict[str, Any]) -> None:
        """Merge data into an existing session."""
        with self._lock:
            if session_id in self._sessions:
                self._sessions[session_id].update(data)
                self._timestamps[session_id] = time.monotonic()

    def delete(self, session_id: str) -> None:
        """Remove a session."""
        with self._lock:
            self._delete_unlocked(session_id)

    def purge_expired(self) -> int:
        """Remove all expired sessions. Returns count of purged sessions."""
        with self._lock:
            return self._purge_expired_unlocked()

    def list_ids(self) -> list[str]:
        """Return all non-expired session IDs."""
        with self._lock:
            now = time.monotonic()
            return [
                sid
                for sid, ts in self._timestamps.items()
                if (now - ts) <= self._max_age
            ]

    def count(self) -> int:
        """Return number of non-expired sessions."""
        return len(self.list_ids())

    def _delete_unlocked(self, session_id: str) -> None:
        """Remove a session (caller must hold self._lock)."""
        self._sessions.pop(session_id, None)
        self._timestamps.pop(session_id, None)

    def _purge_expired_unlocked(self) -> int:
        """Remove all expired sessions (caller must hold self._lock)."""
        now = time.monotonic()
        expired = [
            sid
            for sid, ts in self._timestamps.items()
            if (now - ts) > self._max_age
        ]
        for sid in expired:
            self._delete_unlocked(sid)
        return len(expired)
