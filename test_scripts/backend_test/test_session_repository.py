import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from backend.entity.pojo.Base import Base
from backend.entity.pojo.Session import SessionPOJO
from backend.repository.SessionRepository import SessionRepository
from backend.exception.Exceptions import DatabaseException


@pytest.fixture
def test_db():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def session_repository(test_db):
    repo = SessionRepository()
    repo.db = test_db
    return repo


class TestSessionRepository:
    
    def test_create_session(self, session_repository):
        session = session_repository.create()
        assert session is not None
        assert session.id is not None
        assert session.status == "active"
    
    def test_get_session_by_session_id(self, session_repository):
        created_session = session_repository.create()
        found_session = session_repository.get_session_by_session_id(created_session.id)
        assert found_session is not None
        assert found_session.id == created_session.id
    
    def test_get_session_by_session_id_not_found(self, session_repository):
        found_session = session_repository.get_session_by_session_id(999)
        assert found_session is None
    
    def test_get_active_sessions(self, session_repository):
        session1 = session_repository.create()
        session2 = session_repository.create()
        
        active_sessions = session_repository.get_active_sessions()
        assert len(active_sessions) >= 2
        assert all(s.status == "active" for s in active_sessions)
    
    def test_get_all_sessions(self, session_repository):
        session_repository.create()
        session_repository.create()
        
        all_sessions = session_repository.get_all_sessions()
        assert len(all_sessions) >= 2
    
    def test_delete_session(self, session_repository):
        session = session_repository.create()
        session_repository.delete(session.id)
        
        updated_session = session_repository.get_session_by_session_id(session.id)
        assert updated_session is not None
        assert updated_session.status == "deleted"
    
    def test_update_session(self, session_repository):
        session = session_repository.create()
        update_data = {"status": "archived"}
        session_repository.update_session(session.id, update_data)
        
        updated_session = session_repository.get_session_by_session_id(session.id)
        assert updated_session.status == "archived"
    
    def test_archive_session(self, session_repository):
        session = session_repository.create()
        session_repository.archive_session(session.id)
        
        archived_session = session_repository.get_session_by_session_id(session.id)
        assert archived_session.status == "archived"
    
    def test_update_last_activity(self, session_repository):
        session = session_repository.create()
        original_activity = session.last_activity_at
        
        import time
        time.sleep(0.1)
        
        session_repository.update_last_activity(session.id)
        
        updated_session = session_repository.get_session_by_session_id(session.id)
        assert updated_session.last_activity_at > original_activity