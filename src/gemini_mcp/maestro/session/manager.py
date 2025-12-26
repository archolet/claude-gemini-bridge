"""
Session Manager - TTL and limits for MAESTRO sessions.

Provides production-ready session management with:
- Automatic expiration (TTL)
- Concurrent session limits
- Lazy cleanup on access
"""
from __future__ import annotations

import logging
import time
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from gemini_mcp.maestro.models import MaestroSession

logger = logging.getLogger(__name__)


class SessionManager:
    """
    Manages MAESTRO sessions with TTL and limits.

    Features:
    - Sessions expire after DEFAULT_TTL seconds (1 hour)
    - Maximum MAX_SESSIONS concurrent sessions (100)
    - Lazy cleanup on create/get operations
    - Thread-safe for single-threaded async context

    Usage:
        manager = SessionManager()
        manager.create(session)
        session = manager.get(session_id)
        manager.delete(session_id)
    """

    DEFAULT_TTL: int = 3600  # 1 hour
    MAX_SESSIONS: int = 100  # Global limit

    def __init__(self, ttl: int | None = None, max_sessions: int | None = None):
        """
        Initialize SessionManager.

        Args:
            ttl: Session TTL in seconds (default: 3600)
            max_sessions: Max concurrent sessions (default: 100)
        """
        self._sessions: dict[str, "MaestroSession"] = {}
        self._timestamps: dict[str, float] = {}
        self._ttl = ttl or self.DEFAULT_TTL
        self._max_sessions = max_sessions or self.MAX_SESSIONS

    def create(self, session: "MaestroSession") -> str:
        """
        Register a new session.

        Performs lazy cleanup of expired sessions and enforces limits
        before adding the new session.

        Args:
            session: MaestroSession to register

        Returns:
            Session ID

        Note:
            If max sessions is reached, oldest sessions are removed
            to make room for the new one.
        """
        self._cleanup_expired()
        self._enforce_limits()

        self._sessions[session.session_id] = session
        self._timestamps[session.session_id] = time.time()

        logger.info(
            f"[SessionManager] Created session: {session.session_id} "
            f"(active: {len(self._sessions)})"
        )
        return session.session_id

    def get(self, session_id: str) -> "MaestroSession | None":
        """
        Get session by ID, returns None if expired or not found.

        Automatically removes expired sessions when accessed.

        Args:
            session_id: Session ID to retrieve

        Returns:
            MaestroSession or None if not found/expired
        """
        if session_id not in self._sessions:
            return None

        if self._is_expired(session_id):
            logger.info(f"[SessionManager] Session expired: {session_id}")
            self.delete(session_id)
            return None

        # Update access time for LRU-style behavior (optional)
        # self._timestamps[session_id] = time.time()

        return self._sessions[session_id]

    def delete(self, session_id: str) -> bool:
        """
        Delete a session.

        Args:
            session_id: Session ID to delete

        Returns:
            True if deleted, False if not found
        """
        if session_id not in self._sessions:
            return False

        del self._sessions[session_id]
        del self._timestamps[session_id]

        logger.info(f"[SessionManager] Deleted session: {session_id}")
        return True

    def touch(self, session_id: str) -> bool:
        """
        Update session timestamp to extend its TTL.

        Useful for keeping active sessions alive during long interviews.

        Args:
            session_id: Session ID to touch

        Returns:
            True if session exists and was touched, False otherwise
        """
        if session_id not in self._sessions:
            return False

        if self._is_expired(session_id):
            self.delete(session_id)
            return False

        self._timestamps[session_id] = time.time()
        return True

    def _is_expired(self, session_id: str) -> bool:
        """Check if session has expired based on TTL."""
        created = self._timestamps.get(session_id, 0)
        return (time.time() - created) > self._ttl

    def _cleanup_expired(self) -> int:
        """
        Remove all expired sessions.

        Called lazily on create/get operations.

        Returns:
            Count of removed sessions
        """
        expired = [sid for sid in list(self._sessions) if self._is_expired(sid)]
        for sid in expired:
            self.delete(sid)

        if expired:
            logger.info(f"[SessionManager] Cleaned up {len(expired)} expired sessions")

        return len(expired)

    def _enforce_limits(self) -> None:
        """
        Remove oldest sessions if limit exceeded.

        Uses FIFO strategy - oldest sessions are removed first.
        """
        while len(self._sessions) >= self._max_sessions:
            # Find oldest session by timestamp
            oldest = min(self._timestamps, key=self._timestamps.get)
            logger.warning(
                f"[SessionManager] Limit reached ({self._max_sessions}), "
                f"removing oldest: {oldest}"
            )
            self.delete(oldest)

    @property
    def active_count(self) -> int:
        """Return count of active (non-expired) sessions."""
        self._cleanup_expired()
        return len(self._sessions)

    def list_sessions(self) -> list[str]:
        """
        Return list of active session IDs.

        Performs cleanup before returning the list.

        Returns:
            List of active session IDs
        """
        self._cleanup_expired()
        return list(self._sessions.keys())

    def get_session_info(self, session_id: str) -> dict | None:
        """
        Get session metadata without returning the full session object.

        Args:
            session_id: Session ID to query

        Returns:
            Dict with session metadata or None if not found
        """
        if session_id not in self._sessions:
            return None

        if self._is_expired(session_id):
            return None

        session = self._sessions[session_id]
        created = self._timestamps[session_id]
        age = time.time() - created
        remaining = max(0, self._ttl - age)

        return {
            "session_id": session_id,
            "status": session.state.status.value,
            "age_seconds": int(age),
            "remaining_seconds": int(remaining),
            "answer_count": len(session.state.answers),
            "has_previous_html": bool(session.context.previous_html),
        }

    def cleanup_all(self) -> int:
        """
        Remove all sessions (for shutdown/reset).

        Returns:
            Count of removed sessions
        """
        count = len(self._sessions)
        self._sessions.clear()
        self._timestamps.clear()
        logger.info(f"[SessionManager] Cleaned up all {count} sessions")
        return count
