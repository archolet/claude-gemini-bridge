"""
Tests for MAESTRO Phase 5: SessionManager.

Tests cover:
- Session creation and retrieval
- TTL-based expiration
- Concurrent session limits
- Lazy cleanup on access
"""
from __future__ import annotations

import pytest
import time
from unittest.mock import MagicMock

from gemini_mcp.maestro.session import SessionManager


# =============================================================================
# FIXTURES
# =============================================================================


@pytest.fixture
def manager():
    """Create SessionManager with short TTL for testing."""
    return SessionManager(ttl=60, max_sessions=5)


@pytest.fixture
def mock_session():
    """Create mock MaestroSession."""
    session = MagicMock()
    session.session_id = "test_session_123"
    session.state.status.value = "interviewing"
    session.state.answers = []
    session.context.previous_html = None
    return session


@pytest.fixture
def mock_session_factory():
    """Factory to create multiple mock sessions."""
    def factory(session_id: str):
        session = MagicMock()
        session.session_id = session_id
        session.state.status.value = "interviewing"
        session.state.answers = []
        session.context.previous_html = None
        return session
    return factory


# =============================================================================
# BASIC OPERATIONS
# =============================================================================


class TestSessionManagerBasics:
    """Tests for basic SessionManager operations."""

    def test_create_session(self, manager, mock_session):
        """Test session creation."""
        session_id = manager.create(mock_session)

        assert session_id == "test_session_123"
        assert manager.active_count == 1

    def test_get_existing_session(self, manager, mock_session):
        """Test retrieving existing session."""
        manager.create(mock_session)
        retrieved = manager.get("test_session_123")

        assert retrieved == mock_session

    def test_get_nonexistent_returns_none(self, manager):
        """Test get returns None for nonexistent session."""
        result = manager.get("nonexistent_session")

        assert result is None

    def test_delete_session(self, manager, mock_session):
        """Test session deletion."""
        manager.create(mock_session)
        result = manager.delete("test_session_123")

        assert result is True
        assert manager.active_count == 0

    def test_delete_nonexistent_returns_false(self, manager):
        """Test delete returns False for nonexistent session."""
        result = manager.delete("nonexistent")

        assert result is False

    def test_list_sessions(self, manager, mock_session):
        """Test listing all session IDs."""
        manager.create(mock_session)
        sessions = manager.list_sessions()

        assert "test_session_123" in sessions
        assert len(sessions) == 1


# =============================================================================
# TTL EXPIRATION
# =============================================================================


class TestSessionManagerTTL:
    """Tests for TTL-based session expiration."""

    def test_expired_session_returns_none(self):
        """Test expired session returns None on get."""
        manager = SessionManager(ttl=60)
        session = MagicMock()
        session.session_id = "expiring"

        # Manually add session with past timestamp
        manager._sessions["expiring"] = session
        manager._timestamps["expiring"] = time.time() - 120  # 2 minutes ago

        # Session should be expired
        result = manager.get("expiring")
        assert result is None

    def test_cleanup_removes_expired(self):
        """Test _cleanup_expired removes old sessions."""
        manager = SessionManager(ttl=60)
        session = MagicMock()
        session.session_id = "old_session"

        # Manually add session with past timestamp
        manager._sessions["old_session"] = session
        manager._timestamps["old_session"] = time.time() - 120  # 2 minutes ago

        count = manager._cleanup_expired()

        assert count == 1
        assert manager.active_count == 0

    def test_touch_extends_ttl(self, manager, mock_session):
        """Test touch updates session timestamp."""
        manager.create(mock_session)
        original_ts = manager._timestamps["test_session_123"]

        time.sleep(0.01)  # Small delay
        result = manager.touch("test_session_123")

        assert result is True
        assert manager._timestamps["test_session_123"] > original_ts

    def test_touch_nonexistent_returns_false(self, manager):
        """Test touch returns False for nonexistent session."""
        result = manager.touch("nonexistent")

        assert result is False


# =============================================================================
# SESSION LIMITS
# =============================================================================


class TestSessionManagerLimits:
    """Tests for concurrent session limits."""

    def test_enforce_max_sessions(self, mock_session_factory):
        """Test oldest sessions removed when limit reached."""
        manager = SessionManager(ttl=3600, max_sessions=3)

        # Create 5 sessions (limit is 3)
        for i in range(5):
            session = mock_session_factory(f"session_{i}")
            manager.create(session)
            time.sleep(0.01)  # Ensure different timestamps

        # Should only have 3 sessions
        assert manager.active_count <= 3

    def test_oldest_removed_first(self, mock_session_factory):
        """Test FIFO - oldest sessions removed first."""
        manager = SessionManager(ttl=3600, max_sessions=2)

        # Create first session
        session1 = mock_session_factory("session_oldest")
        manager.create(session1)
        time.sleep(0.01)

        # Create second session
        session2 = mock_session_factory("session_middle")
        manager.create(session2)
        time.sleep(0.01)

        # Create third session (should trigger removal of oldest)
        session3 = mock_session_factory("session_newest")
        manager.create(session3)

        # Oldest should be removed
        assert manager.get("session_oldest") is None
        # Newest should exist
        assert manager.get("session_newest") is not None


# =============================================================================
# SESSION INFO
# =============================================================================


class TestSessionManagerInfo:
    """Tests for session metadata retrieval."""

    def test_get_session_info(self, manager, mock_session):
        """Test get_session_info returns metadata dict."""
        manager.create(mock_session)
        info = manager.get_session_info("test_session_123")

        assert info is not None
        assert info["session_id"] == "test_session_123"
        assert "status" in info
        assert "age_seconds" in info
        assert "remaining_seconds" in info
        assert "answer_count" in info
        assert "has_previous_html" in info

    def test_get_session_info_nonexistent(self, manager):
        """Test get_session_info returns None for nonexistent."""
        info = manager.get_session_info("nonexistent")

        assert info is None

    def test_get_session_info_expired(self):
        """Test get_session_info returns None for expired session."""
        manager = SessionManager(ttl=60)
        session = MagicMock()
        session.session_id = "expired"

        # Manually add session with past timestamp
        manager._sessions["expired"] = session
        manager._timestamps["expired"] = time.time() - 120  # 2 minutes ago

        info = manager.get_session_info("expired")
        assert info is None


# =============================================================================
# CLEANUP ALL
# =============================================================================


class TestSessionManagerCleanupAll:
    """Tests for cleanup_all operation."""

    def test_cleanup_all_removes_all(self, manager, mock_session_factory):
        """Test cleanup_all removes all sessions."""
        for i in range(5):
            session = mock_session_factory(f"session_{i}")
            manager.create(session)

        count = manager.cleanup_all()

        assert count == 5
        assert manager.active_count == 0

    def test_cleanup_all_empty(self, manager):
        """Test cleanup_all with no sessions."""
        count = manager.cleanup_all()

        assert count == 0


# =============================================================================
# CONFIGURATION
# =============================================================================


class TestSessionManagerConfig:
    """Tests for SessionManager configuration."""

    def test_default_ttl(self):
        """Test default TTL is 3600 seconds."""
        manager = SessionManager()
        assert manager._ttl == 3600

    def test_default_max_sessions(self):
        """Test default max sessions is 100."""
        manager = SessionManager()
        assert manager._max_sessions == 100

    def test_custom_ttl(self):
        """Test custom TTL configuration."""
        manager = SessionManager(ttl=1800)
        assert manager._ttl == 1800

    def test_custom_max_sessions(self):
        """Test custom max sessions configuration."""
        manager = SessionManager(max_sessions=50)
        assert manager._max_sessions == 50
