"""
Session Management for BasicChat Application
Provides persistent storage and management of chat sessions
"""

import os
import json
import sqlite3
import uuid
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any, Tuple
from dataclasses import dataclass, field, asdict
from pathlib import Path
import logging
from contextlib import contextmanager

from src.config import config
from src.database.database_migrations import run_migrations, get_migration_status

logger = logging.getLogger(__name__)

@dataclass
class ChatSession:
    """Represents a chat session with all metadata and messages"""
    id: str
    title: str
    created_at: datetime
    updated_at: datetime
    model_used: str
    reasoning_mode: str
    messages: List[Dict[str, str]]
    metadata: Dict[str, Any] = field(default_factory=dict)
    is_archived: bool = False
    tags: List[str] = field(default_factory=list)
    user_id: str = "default"

@dataclass
class SessionMetadata:
    """Additional metadata for chat sessions"""
    document_count: int = 0
    total_messages: int = 0
    session_duration: Optional[timedelta] = None
    reasoning_steps_count: int = 0
    audio_generated: bool = False
    tools_used: List[str] = field(default_factory=list)
    last_activity: Optional[datetime] = None

class SessionManager:
    """Manages chat session storage and retrieval with SQLite backend"""
    
    def __init__(self, db_path: str = None):
        """Initialize session manager with database path"""
        self.db_path = db_path or config.session.database_path
        self._ensure_database_directory()
        self._run_migrations()
    
    def _ensure_database_directory(self):
        """Ensure the database directory exists"""
        db_dir = os.path.dirname(self.db_path)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir, exist_ok=True)
    
    def _run_migrations(self):
        """Run database migrations to ensure schema is up to date"""
        try:
            logger.info("Running database migrations...")
            success = run_migrations(self.db_path)
            if success:
                status = get_migration_status(self.db_path)
                logger.info(f"Database migrations completed. Version: {status['database_version']}")
            else:
                logger.error("Database migrations failed")
                raise Exception("Failed to run database migrations")
        except Exception as e:
            logger.error(f"Error running migrations: {e}")
            raise
    
    @contextmanager
    def _get_connection(self):
        """Context manager for database connections"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Enable column access by name
        try:
            yield conn
        finally:
            conn.close()
    
    def create_session(self, title: str, model: str, reasoning_mode: str, 
                      user_id: str = "default", tags: List[str] = None) -> ChatSession:
        """Create a new chat session"""
        try:
            session_id = str(uuid.uuid4())
            now = datetime.now()
            
            session = ChatSession(
                id=session_id,
                title=title,
                created_at=now,
                updated_at=now,
                model_used=model,
                reasoning_mode=reasoning_mode,
                messages=[],
                metadata=asdict(SessionMetadata()),
                tags=tags or [],
                user_id=user_id
            )
            
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO chat_sessions 
                    (id, title, created_at, updated_at, model_used, reasoning_mode, 
                     messages, metadata, tags, user_id)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    session.id, session.title, session.created_at, session.updated_at,
                    session.model_used, session.reasoning_mode, 
                    json.dumps(session.messages), json.dumps(session.metadata),
                    json.dumps(session.tags), session.user_id
                ))
                conn.commit()
            
            logger.info(f"Created new session: {session_id}")
            return session
            
        except Exception as e:
            logger.error(f"Failed to create session: {e}")
            raise
    
    def save_session(self, session: ChatSession) -> bool:
        """Save or update a chat session"""
        try:
            session.updated_at = datetime.now()
            
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT OR REPLACE INTO chat_sessions 
                    (id, title, created_at, updated_at, model_used, reasoning_mode, 
                     messages, metadata, is_archived, tags, user_id)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    session.id, session.title, session.created_at, session.updated_at,
                    session.model_used, session.reasoning_mode, 
                    json.dumps(session.messages), json.dumps(session.metadata),
                    session.is_archived, json.dumps(session.tags), session.user_id
                ))
                conn.commit()
            
            logger.debug(f"Saved session: {session.id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save session {session.id}: {e}")
            return False
    
    def load_session(self, session_id: str) -> Optional[ChatSession]:
        """Load a chat session by ID"""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT * FROM chat_sessions WHERE id = ?
                """, (session_id,))
                
                row = cursor.fetchone()
                if not row:
                    return None
                
                session = ChatSession(
                    id=row['id'],
                    title=row['title'],
                    created_at=datetime.fromisoformat(row['created_at']),
                    updated_at=datetime.fromisoformat(row['updated_at']),
                    model_used=row['model_used'],
                    reasoning_mode=row['reasoning_mode'],
                    messages=json.loads(row['messages']),
                    metadata=json.loads(row['metadata']) if row['metadata'] else {},
                    is_archived=bool(row['is_archived']),
                    tags=json.loads(row['tags']) if row['tags'] else [],
                    user_id=row['user_id']
                )
                
                return session
                
        except Exception as e:
            logger.error(f"Failed to load session {session_id}: {e}")
            return None
    
    def list_sessions(self, user_id: str = "default", archived: bool = False, 
                     limit: int = 50, offset: int = 0) -> List[ChatSession]:
        """List chat sessions with pagination and filtering"""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT * FROM chat_sessions 
                    WHERE user_id = ? AND is_archived = ?
                    ORDER BY updated_at DESC
                    LIMIT ? OFFSET ?
                """, (user_id, archived, limit, offset))
                
                sessions = []
                for row in cursor.fetchall():
                    session = ChatSession(
                        id=row['id'],
                        title=row['title'],
                        created_at=datetime.fromisoformat(row['created_at']),
                        updated_at=datetime.fromisoformat(row['updated_at']),
                        model_used=row['model_used'],
                        reasoning_mode=row['reasoning_mode'],
                        messages=json.loads(row['messages']),
                        metadata=json.loads(row['metadata']) if row['metadata'] else {},
                        is_archived=bool(row['is_archived']),
                        tags=json.loads(row['tags']) if row['tags'] else [],
                        user_id=row['user_id']
                    )
                    sessions.append(session)
                
                return sessions
                
        except Exception as e:
            logger.error(f"Failed to list sessions: {e}")
            return []
    
    def update_session(self, session_id: str, updates: Dict[str, Any]) -> bool:
        """Update session fields"""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                # Build dynamic update query
                set_clauses = []
                values = []
                
                for key, value in updates.items():
                    if key in ['title', 'model_used', 'reasoning_mode', 'is_archived', 'user_id']:
                        set_clauses.append(f"{key} = ?")
                        values.append(value)
                    elif key in ['messages', 'metadata', 'tags']:
                        set_clauses.append(f"{key} = ?")
                        values.append(json.dumps(value))
                
                if not set_clauses:
                    return False
                
                set_clauses.append("updated_at = ?")
                values.append(datetime.now())
                values.append(session_id)
                
                query = f"""
                    UPDATE chat_sessions 
                    SET {', '.join(set_clauses)}
                    WHERE id = ?
                """
                
                cursor.execute(query, values)
                conn.commit()
                
                logger.debug(f"Updated session: {session_id}")
                return True
                
        except Exception as e:
            logger.error(f"Failed to update session {session_id}: {e}")
            return False
    
    def delete_session(self, session_id: str) -> bool:
        """Delete a chat session"""
        if not session_id or not session_id.strip():
            return False
            
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM chat_sessions WHERE id = ?", (session_id,))
                rows_affected = cursor.rowcount
                conn.commit()
                
                if rows_affected > 0:
                    logger.info(f"Deleted session: {session_id}")
                    return True
                else:
                    logger.warning(f"No session found to delete: {session_id}")
                    return False
                
        except Exception as e:
            logger.error(f"Failed to delete session {session_id}: {e}")
            return False
    
    def search_sessions(self, query: str, user_id: str = "default", 
                       limit: int = 20) -> List[ChatSession]:
        """Search sessions by title and content"""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT * FROM chat_sessions 
                    WHERE user_id = ? AND is_archived = FALSE
                    AND (title LIKE ? OR messages LIKE ?)
                    ORDER BY updated_at DESC
                    LIMIT ?
                """, (user_id, f"%{query}%", f"%{query}%", limit))
                
                sessions = []
                for row in cursor.fetchall():
                    session = ChatSession(
                        id=row['id'],
                        title=row['title'],
                        created_at=datetime.fromisoformat(row['created_at']),
                        updated_at=datetime.fromisoformat(row['updated_at']),
                        model_used=row['model_used'],
                        reasoning_mode=row['reasoning_mode'],
                        messages=json.loads(row['messages']),
                        metadata=json.loads(row['metadata']) if row['metadata'] else {},
                        is_archived=bool(row['is_archived']),
                        tags=json.loads(row['tags']) if row['tags'] else [],
                        user_id=row['user_id']
                    )
                    sessions.append(session)
                
                return sessions
                
        except Exception as e:
            logger.error(f"Failed to search sessions: {e}")
            return []
    
    def export_session(self, session_id: str, format: str = "json") -> Optional[str]:
        """Export session in specified format"""
        try:
            session = self.load_session(session_id)
            if not session:
                return None
            
            if format.lower() == "json":
                return json.dumps(asdict(session), default=str, indent=2)
            elif format.lower() == "markdown":
                return self._export_to_markdown(session)
            else:
                raise ValueError(f"Unsupported export format: {format}")
                
        except Exception as e:
            logger.error(f"Failed to export session {session_id}: {e}")
            return None
    
    def _export_to_markdown(self, session: ChatSession) -> str:
        """Export session to markdown format"""
        md_content = f"""# {session.title}

**Session Details:**
- **Created:** {session.created_at.strftime('%Y-%m-%d %H:%M:%S')}
- **Updated:** {session.updated_at.strftime('%Y-%m-%d %H:%M:%S')}
- **Model:** {session.model_used}
- **Reasoning Mode:** {session.reasoning_mode}
- **Tags:** {', '.join(session.tags) if session.tags else 'None'}

## Conversation

"""
        
        for msg in session.messages:
            role = msg.get('role', 'unknown')
            content = msg.get('content', '')
            
            if role == 'user':
                md_content += f"### 👤 User\n{content}\n\n"
            elif role == 'assistant':
                md_content += f"### 🤖 Assistant\n{content}\n\n"
        
        return md_content
    
    def import_session(self, session_data: str, format: str = "json") -> Optional[ChatSession]:
        """Import session from specified format"""
        try:
            if format.lower() == "json":
                data = json.loads(session_data)
                # Generate new ID for imported session
                data['id'] = str(uuid.uuid4())
                data['created_at'] = datetime.now()
                data['updated_at'] = datetime.now()
                
                session = ChatSession(**data)
                self.save_session(session)
                return session
            else:
                raise ValueError(f"Unsupported import format: {format}")
                
        except Exception as e:
            logger.error(f"Failed to import session: {e}")
            return None
    
    def auto_save_session(self, session_id: str, messages: List[Dict[str, str]]) -> bool:
        """Auto-save session with updated messages"""
        try:
            session = self.load_session(session_id)
            if not session:
                return False
            
            session.messages = messages
            session.updated_at = datetime.now()
            
            # Update metadata
            metadata = session.metadata
            metadata['total_messages'] = len(messages)
            metadata['last_activity'] = datetime.now().isoformat()
            
            # Count reasoning steps
            reasoning_steps = sum(1 for msg in messages 
                                if 'reasoning_steps' in msg.get('metadata', {}))
            metadata['reasoning_steps_count'] = reasoning_steps
            
            return self.save_session(session)
            
        except Exception as e:
            logger.error(f"Failed to auto-save session {session_id}: {e}")
            return False
    
    def get_session_stats(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get statistics for a session"""
        try:
            session = self.load_session(session_id)
            if not session:
                return None
            
            stats = {
                'id': session.id,
                'title': session.title,
                'created_at': session.created_at,
                'updated_at': session.updated_at,
                'model_used': session.model_used,
                'reasoning_mode': session.reasoning_mode,
                'total_messages': len(session.messages),
                'user_messages': len([m for m in session.messages if m.get('role') == 'user']),
                'assistant_messages': len([m for m in session.messages if m.get('role') == 'assistant']),
                'session_duration': session.updated_at - session.created_at,
                'is_archived': session.is_archived,
                'tags': session.tags,
                'metadata': session.metadata
            }
            
            return stats
            
        except Exception as e:
            logger.error(f"Failed to get stats for session {session_id}: {e}")
            return None
    
    def cleanup_old_sessions(self, days: int = 30) -> int:
        """Clean up sessions older than specified days"""
        try:
            cutoff_date = datetime.now() - timedelta(days=days)
            
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    DELETE FROM chat_sessions 
                    WHERE created_at < ? AND is_archived = TRUE
                """, (cutoff_date,))
                
                deleted_count = cursor.rowcount
                conn.commit()
                
                logger.info(f"Cleaned up {deleted_count} old sessions")
                return deleted_count
                
        except Exception as e:
            logger.error(f"Failed to cleanup old sessions: {e}")
            return 0
    
    def get_database_stats(self) -> Dict[str, Any]:
        """Get database statistics"""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                # Total sessions
                cursor.execute("SELECT COUNT(*) FROM chat_sessions")
                total_sessions = cursor.fetchone()[0]
                
                # Active sessions
                cursor.execute("SELECT COUNT(*) FROM chat_sessions WHERE is_archived = FALSE")
                active_sessions = cursor.fetchone()[0]
                
                # Archived sessions
                cursor.execute("SELECT COUNT(*) FROM chat_sessions WHERE is_archived = TRUE")
                archived_sessions = cursor.fetchone()[0]
                
                # Database size
                db_size = os.path.getsize(self.db_path) if os.path.exists(self.db_path) else 0
                
                return {
                    'total_sessions': total_sessions,
                    'active_sessions': active_sessions,
                    'archived_sessions': archived_sessions,
                    'database_size_bytes': db_size,
                    'database_size_mb': round(db_size / (1024 * 1024), 2)
                }
                
        except Exception as e:
            logger.error(f"Failed to get database stats: {e}")
            return {}

# Global session manager instance
session_manager = SessionManager() 