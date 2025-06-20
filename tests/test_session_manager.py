"""
Tests for Session Manager functionality
"""

import pytest
import os
import json
import tempfile
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock

from src.session import SessionManager, ChatSession, SessionMetadata
from src.database import run_migrations


@pytest.fixture
def temp_db_path():
    """Create a temporary database path for testing"""
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
        db_path = tmp.name
    yield db_path
    # Cleanup
    if os.path.exists(db_path):
        os.unlink(db_path)


@pytest.fixture
def session_manager(temp_db_path):
    """Create a session manager with temporary database"""
    # Run migrations to create the schema
    run_migrations(temp_db_path)
    return SessionManager(temp_db_path)


@pytest.fixture
def sample_session_data():
    """Sample session data for testing"""
    return {
        "title": "Test Session",
        "model_used": "mistral",
        "reasoning_mode": "Standard",
        "messages": [
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi there!"}
        ],
        "tags": ["test", "sample"]
    }


class TestChatSession:
    """Test ChatSession dataclass"""
    
    def test_chat_session_creation(self):
        """Test creating a ChatSession instance"""
        now = datetime.now()
        session = ChatSession(
            id="test-id",
            title="Test Session",
            created_at=now,
            updated_at=now,
            model_used="mistral",
            reasoning_mode="Standard",
            messages=[{"role": "user", "content": "Hello"}]
        )
        
        assert session.id == "test-id"
        assert session.title == "Test Session"
        assert session.model_used == "mistral"
        assert session.reasoning_mode == "Standard"
        assert len(session.messages) == 1
        assert session.is_archived is False
        assert session.tags == []
        assert session.user_id == "default"
    
    def test_chat_session_with_optional_fields(self):
        """Test ChatSession with optional fields"""
        now = datetime.now()
        session = ChatSession(
            id="test-id",
            title="Test Session",
            created_at=now,
            updated_at=now,
            model_used="mistral",
            reasoning_mode="Standard",
            messages=[],
            metadata={"test": "data"},
            is_archived=True,
            tags=["tag1", "tag2"],
            user_id="user123"
        )
        
        assert session.metadata == {"test": "data"}
        assert session.is_archived is True
        assert session.tags == ["tag1", "tag2"]
        assert session.user_id == "user123"


class TestSessionMetadata:
    """Test SessionMetadata dataclass"""
    
    def test_session_metadata_defaults(self):
        """Test SessionMetadata with default values"""
        metadata = SessionMetadata()
        
        assert metadata.document_count == 0
        assert metadata.total_messages == 0
        assert metadata.session_duration is None
        assert metadata.reasoning_steps_count == 0
        assert metadata.audio_generated is False
        assert metadata.tools_used == []
        assert metadata.last_activity is None
    
    def test_session_metadata_with_values(self):
        """Test SessionMetadata with custom values"""
        duration = timedelta(hours=1)
        now = datetime.now()
        
        metadata = SessionMetadata(
            document_count=5,
            total_messages=20,
            session_duration=duration,
            reasoning_steps_count=10,
            audio_generated=True,
            tools_used=["calculator", "web_search"],
            last_activity=now
        )
        
        assert metadata.document_count == 5
        assert metadata.total_messages == 20
        assert metadata.session_duration == duration
        assert metadata.reasoning_steps_count == 10
        assert metadata.audio_generated is True
        assert metadata.tools_used == ["calculator", "web_search"]
        assert metadata.last_activity == now


class TestSessionManager:
    """Test SessionManager functionality"""
    
    def test_session_manager_initialization(self, temp_db_path):
        """Test SessionManager initialization"""
        manager = SessionManager(db_path=temp_db_path)
        
        assert manager.db_path == temp_db_path
        assert os.path.exists(temp_db_path)
    
    def test_create_session(self, session_manager, sample_session_data):
        """Test creating a new session"""
        session = session_manager.create_session(
            title=sample_session_data["title"],
            model=sample_session_data["model_used"],
            reasoning_mode=sample_session_data["reasoning_mode"],
            tags=sample_session_data["tags"]
        )
        
        assert session.id is not None
        assert session.title == sample_session_data["title"]
        assert session.model_used == sample_session_data["model_used"]
        assert session.reasoning_mode == sample_session_data["reasoning_mode"]
        assert session.tags == sample_session_data["tags"]
        assert session.messages == []
        assert session.is_archived is False
        assert session.user_id == "default"
    
    def test_save_and_load_session(self, session_manager, sample_session_data):
        """Test saving and loading a session"""
        # Create session
        session = session_manager.create_session(
            title=sample_session_data["title"],
            model=sample_session_data["model_used"],
            reasoning_mode=sample_session_data["reasoning_mode"]
        )
        
        # Add messages
        session.messages = sample_session_data["messages"]
        
        # Save session
        assert session_manager.save_session(session) is True
        
        # Load session
        loaded_session = session_manager.load_session(session.id)
        
        assert loaded_session is not None
        assert loaded_session.id == session.id
        assert loaded_session.title == session.title
        assert loaded_session.messages == sample_session_data["messages"]
    
    def test_load_nonexistent_session(self, session_manager):
        """Test loading a session that doesn't exist"""
        session = session_manager.load_session("nonexistent-id")
        assert session is None
    
    def test_list_sessions(self, session_manager, sample_session_data):
        """Test listing sessions"""
        # Create multiple sessions
        session1 = session_manager.create_session(
            title="Session 1",
            model="mistral",
            reasoning_mode="Standard"
        )
        session2 = session_manager.create_session(
            title="Session 2",
            model="llama2",
            reasoning_mode="Chain-of-Thought"
        )
        
        # List active sessions
        sessions = session_manager.list_sessions()
        
        assert len(sessions) == 2
        session_ids = [s.id for s in sessions]
        assert session1.id in session_ids
        assert session2.id in session_ids
    
    def test_list_sessions_with_pagination(self, session_manager):
        """Test listing sessions with pagination"""
        # Create multiple sessions
        for i in range(5):
            session_manager.create_session(
                title=f"Session {i}",
                model="mistral",
                reasoning_mode="Standard"
            )
        
        # Test pagination
        sessions = session_manager.list_sessions(limit=3, offset=0)
        assert len(sessions) == 3
        
        sessions = session_manager.list_sessions(limit=3, offset=3)
        assert len(sessions) == 2
    
    def test_update_session(self, session_manager, sample_session_data):
        """Test updating session fields"""
        session = session_manager.create_session(
            title=sample_session_data["title"],
            model=sample_session_data["model_used"],
            reasoning_mode=sample_session_data["reasoning_mode"]
        )
        
        # Update session
        updates = {
            "title": "Updated Title",
            "model_used": "llama2",
            "is_archived": True
        }
        
        assert session_manager.update_session(session.id, updates) is True
        
        # Load and verify updates
        updated_session = session_manager.load_session(session.id)
        assert updated_session.title == "Updated Title"
        assert updated_session.model_used == "llama2"
        assert updated_session.is_archived is True
    
    def test_delete_session(self, session_manager, sample_session_data):
        """Test deleting a session"""
        session = session_manager.create_session(
            title=sample_session_data["title"],
            model=sample_session_data["model_used"],
            reasoning_mode=sample_session_data["reasoning_mode"]
        )
        
        # Verify session exists
        assert session_manager.load_session(session.id) is not None
        
        # Delete session
        assert session_manager.delete_session(session.id) is True
        
        # Verify session is deleted
        assert session_manager.load_session(session.id) is None
    
    def test_search_sessions(self, session_manager):
        """Test searching sessions"""
        # Create sessions with different content
        session1 = session_manager.create_session(
            title="Python Programming",
            model="mistral",
            reasoning_mode="Standard"
        )
        session1.messages = [{"role": "user", "content": "How to use Python?"}]
        session_manager.save_session(session1)
        
        session2 = session_manager.create_session(
            title="JavaScript Basics",
            model="llama2",
            reasoning_mode="Chain-of-Thought"
        )
        session2.messages = [{"role": "user", "content": "JavaScript tutorial"}]
        session_manager.save_session(session2)
        
        # Search for Python
        results = session_manager.search_sessions("Python")
        assert len(results) == 1
        assert results[0].id == session1.id
        
        # Search for JavaScript
        results = session_manager.search_sessions("JavaScript")
        assert len(results) == 1
        assert results[0].id == session2.id
    
    def test_export_session_json(self, session_manager, sample_session_data):
        """Test exporting session to JSON format"""
        session = session_manager.create_session(
            title=sample_session_data["title"],
            model=sample_session_data["model_used"],
            reasoning_mode=sample_session_data["reasoning_mode"]
        )
        session.messages = sample_session_data["messages"]
        session_manager.save_session(session)
        
        # Export to JSON
        json_data = session_manager.export_session(session.id, "json")
        
        assert json_data is not None
        exported_data = json.loads(json_data)
        assert exported_data["title"] == sample_session_data["title"]
        assert exported_data["model_used"] == sample_session_data["model_used"]
        assert exported_data["messages"] == sample_session_data["messages"]
    
    def test_export_session_markdown(self, session_manager, sample_session_data):
        """Test exporting session to Markdown format"""
        session = session_manager.create_session(
            title=sample_session_data["title"],
            model=sample_session_data["model_used"],
            reasoning_mode=sample_session_data["reasoning_mode"]
        )
        session.messages = sample_session_data["messages"]
        session_manager.save_session(session)
        
        # Export to Markdown
        md_data = session_manager.export_session(session.id, "markdown")
        
        assert md_data is not None
        assert "# Test Session" in md_data
        assert "👤 User" in md_data
        assert "🤖 Assistant" in md_data
        assert "Hello" in md_data
        assert "Hi there!" in md_data
    
    def test_export_invalid_format(self, session_manager, sample_session_data):
        """Test exporting with invalid format"""
        session = session_manager.create_session(
            title=sample_session_data["title"],
            model=sample_session_data["model_used"],
            reasoning_mode=sample_session_data["reasoning_mode"]
        )
        
        # Export with invalid format
        result = session_manager.export_session(session.id, "invalid")
        assert result is None
    
    def test_import_session(self, session_manager, sample_session_data):
        """Test importing a session"""
        # Create session data for import
        import_data = {
            "id": "imported-id",
            "title": "Imported Session",
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "model_used": "llama2",
            "reasoning_mode": "Multi-Step",
            "messages": sample_session_data["messages"],
            "metadata": {},
            "is_archived": False,
            "tags": ["imported"],
            "user_id": "default"
        }
        
        # Import session
        imported_session = session_manager.import_session(
            json.dumps(import_data), "json"
        )
        
        assert imported_session is not None
        assert imported_session.title == "Imported Session"
        assert imported_session.model_used == "llama2"
        assert imported_session.reasoning_mode == "Multi-Step"
        assert imported_session.tags == ["imported"]
        # Should have new ID
        assert imported_session.id != "imported-id"
    
    def test_auto_save_session(self, session_manager, sample_session_data):
        """Test auto-saving session with updated messages"""
        session = session_manager.create_session(
            title=sample_session_data["title"],
            model=sample_session_data["model_used"],
            reasoning_mode=sample_session_data["reasoning_mode"]
        )
        
        # Auto-save with messages
        messages = [
            {"role": "user", "content": "First message"},
            {"role": "assistant", "content": "First response"}
        ]
        
        assert session_manager.auto_save_session(session.id, messages) is True
        
        # Load and verify
        saved_session = session_manager.load_session(session.id)
        assert saved_session.messages == messages
        assert saved_session.metadata["total_messages"] == 2
    
    def test_get_session_stats(self, session_manager, sample_session_data):
        """Test getting session statistics"""
        session = session_manager.create_session(
            title=sample_session_data["title"],
            model=sample_session_data["model_used"],
            reasoning_mode=sample_session_data["reasoning_mode"]
        )
        session.messages = sample_session_data["messages"]
        session_manager.save_session(session)
        
        # Get stats
        stats = session_manager.get_session_stats(session.id)
        
        assert stats is not None
        assert stats["id"] == session.id
        assert stats["title"] == sample_session_data["title"]
        assert stats["total_messages"] == 2
        assert stats["user_messages"] == 1
        assert stats["assistant_messages"] == 1
        assert stats["is_archived"] is False
    
    def test_get_session_stats_nonexistent(self, session_manager):
        """Test getting stats for nonexistent session"""
        stats = session_manager.get_session_stats("nonexistent-id")
        assert stats is None
    
    def test_cleanup_old_sessions(self, session_manager):
        """Test cleaning up old archived sessions"""
        # Create old archived session
        old_session = session_manager.create_session(
            title="Old Session",
            model="mistral",
            reasoning_mode="Standard"
        )
        old_session.is_archived = True
        old_session.created_at = datetime.now() - timedelta(days=40)
        session_manager.save_session(old_session)
        
        # Create recent archived session
        recent_session = session_manager.create_session(
            title="Recent Session",
            model="mistral",
            reasoning_mode="Standard"
        )
        recent_session.is_archived = True
        session_manager.save_session(recent_session)
        
        # Cleanup sessions older than 30 days
        deleted_count = session_manager.cleanup_old_sessions(days=30)
        
        assert deleted_count == 1
        
        # Verify old session is deleted
        assert session_manager.load_session(old_session.id) is None
        
        # Verify recent session still exists
        assert session_manager.load_session(recent_session.id) is not None
    
    def test_get_database_stats(self, session_manager):
        """Test getting database statistics"""
        # Create some sessions
        session_manager.create_session("Session 1", "mistral", "Standard")
        session_manager.create_session("Session 2", "llama2", "Chain-of-Thought")
        
        # Archive one session
        session3 = session_manager.create_session("Session 3", "mistral", "Standard")
        session3.is_archived = True
        session_manager.save_session(session3)
        
        # Get stats
        stats = session_manager.get_database_stats()
        
        assert stats["total_sessions"] == 3
        assert stats["active_sessions"] == 2
        assert stats["archived_sessions"] == 1
        assert stats["database_size_bytes"] > 0
        assert stats["database_size_mb"] > 0
    
    def test_session_manager_error_handling(self, session_manager):
        """Test error handling in session manager"""
        # Test with invalid session ID
        assert session_manager.load_session("") is None
        assert session_manager.delete_session("") is False
        assert session_manager.get_session_stats("") is None
        
        # Test with invalid update data
        session = session_manager.create_session("Test", "mistral", "Standard")
        assert session_manager.update_session(session.id, {}) is False


class TestSessionManagerIntegration:
    """Integration tests for SessionManager"""
    
    def test_full_session_lifecycle(self, session_manager):
        """Test complete session lifecycle"""
        # 1. Create session
        session = session_manager.create_session(
            title="Lifecycle Test",
            model="mistral",
            reasoning_mode="Chain-of-Thought",
            tags=["test", "lifecycle"]
        )
        
        # 2. Add messages over time
        messages = [
            {"role": "user", "content": "Initial question"},
            {"role": "assistant", "content": "Initial response"}
        ]
        session_manager.auto_save_session(session.id, messages)
        
        # 3. Update session
        session_manager.update_session(session.id, {
            "title": "Updated Lifecycle Test"
        })
        
        # 4. Search for session
        results = session_manager.search_sessions("Lifecycle")
        assert len(results) == 1
        assert results[0].id == session.id
        
        # 5. Export session
        json_export = session_manager.export_session(session.id, "json")
        assert json_export is not None
        
        # 6. Archive session
        session_manager.update_session(session.id, {"is_archived": True})
        
        # 7. Verify archived session
        archived_sessions = session_manager.list_sessions(archived=True)
        assert len(archived_sessions) == 1
        assert archived_sessions[0].id == session.id
        
        # 8. Delete session
        assert session_manager.delete_session(session.id) is True
        assert session_manager.load_session(session.id) is None
    
    def test_multiple_users(self, session_manager):
        """Test session isolation between users"""
        # Create sessions for different users
        user1_session = session_manager.create_session(
            "User 1 Session", "mistral", "Standard", user_id="user1"
        )
        user2_session = session_manager.create_session(
            "User 2 Session", "llama2", "Chain-of-Thought", user_id="user2"
        )
        
        # List sessions for each user
        user1_sessions = session_manager.list_sessions(user_id="user1")
        user2_sessions = session_manager.list_sessions(user_id="user2")
        
        assert len(user1_sessions) == 1
        assert len(user2_sessions) == 1
        assert user1_sessions[0].id == user1_session.id
        assert user2_sessions[0].id == user2_session.id
        
        # Verify isolation
        assert user1_sessions[0].user_id == "user1"
        assert user2_sessions[0].user_id == "user2" 