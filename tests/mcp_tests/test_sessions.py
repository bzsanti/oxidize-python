"""F-007 & F-008: Sessions module — CRUD, expiry, and listing."""

import time


class TestSessionStoreCrud:
    def test_create_returns_uuid(self):
        from oxidize_pdf.mcp.sessions import SessionStore

        store = SessionStore()
        session_id = store.create({"title": "Test"})
        assert isinstance(session_id, str)
        assert len(session_id) == 36

    def test_get_returns_data(self):
        from oxidize_pdf.mcp.sessions import SessionStore

        store = SessionStore()
        sid = store.create({"title": "Test"})
        data = store.get(sid)
        assert data["title"] == "Test"

    def test_get_missing_returns_none(self):
        from oxidize_pdf.mcp.sessions import SessionStore

        store = SessionStore()
        assert store.get("nonexistent-id") is None

    def test_update_merges_data(self):
        from oxidize_pdf.mcp.sessions import SessionStore

        store = SessionStore()
        sid = store.create({"pages": []})
        store.update(sid, {"pages": ["p1"]})
        assert store.get(sid)["pages"] == ["p1"]

    def test_delete_removes_session(self):
        from oxidize_pdf.mcp.sessions import SessionStore

        store = SessionStore()
        sid = store.create({})
        store.delete(sid)
        assert store.get(sid) is None


class TestSessionStoreExpiry:
    def test_session_expires_after_max_age(self):
        from oxidize_pdf.mcp.sessions import SessionStore

        store = SessionStore(max_age_seconds=0.01)
        sid = store.create({})
        time.sleep(0.05)
        store.purge_expired()
        assert store.get(sid) is None

    def test_list_ids_returns_all_active(self):
        from oxidize_pdf.mcp.sessions import SessionStore

        store = SessionStore()
        sid1 = store.create({"title": "A"})
        sid2 = store.create({"title": "B"})
        ids = store.list_ids()
        assert sid1 in ids
        assert sid2 in ids

    def test_count(self):
        from oxidize_pdf.mcp.sessions import SessionStore

        store = SessionStore()
        store.create({})
        store.create({})
        assert store.count() == 2

    def test_purge_returns_count(self):
        from oxidize_pdf.mcp.sessions import SessionStore

        store = SessionStore(max_age_seconds=0.01)
        store.create({})
        store.create({})
        time.sleep(0.05)
        purged = store.purge_expired()
        assert purged == 2
        assert store.count() == 0

    def test_get_returns_none_for_expired_without_purge(self):
        """get() must return None for expired sessions even without calling purge_expired()."""
        from oxidize_pdf.mcp.sessions import SessionStore

        store = SessionStore(max_age_seconds=0.01)
        sid = store.create({"title": "Expiring"})
        time.sleep(0.05)
        assert store.get(sid) is None


class TestSessionStoreMaxSessions:
    def test_create_fails_when_at_max_capacity(self):
        import pytest

        from oxidize_pdf.mcp.sessions import SessionLimitError, SessionStore

        store = SessionStore(max_age_seconds=3600, max_sessions=2)
        store.create({"title": "A"})
        store.create({"title": "B"})
        with pytest.raises(SessionLimitError):
            store.create({"title": "C"})

    def test_create_succeeds_after_delete_frees_slot(self):
        from oxidize_pdf.mcp.sessions import SessionStore

        store = SessionStore(max_age_seconds=3600, max_sessions=1)
        sid = store.create({"title": "A"})
        store.delete(sid)
        new_sid = store.create({"title": "B"})
        assert new_sid is not None

    def test_create_auto_purges_expired_before_checking_limit(self):
        from oxidize_pdf.mcp.sessions import SessionStore

        store = SessionStore(max_age_seconds=0.01, max_sessions=2)
        store.create({"title": "A"})
        store.create({"title": "B"})
        time.sleep(0.05)
        # Both expired; create() should purge them first, then succeed
        new_sid = store.create({"title": "C"})
        assert new_sid is not None
        assert store.count() == 1

    def test_no_limit_when_max_sessions_is_zero(self):
        from oxidize_pdf.mcp.sessions import SessionStore

        store = SessionStore(max_age_seconds=3600, max_sessions=0)
        for i in range(50):
            store.create({"i": i})
        assert store.count() == 50
