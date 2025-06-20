"""
Database Migration System for BasicChat
Provides seamless schema versioning and automatic migrations
"""

import os
import sqlite3
import json
import logging
from datetime import datetime
from typing import List, Dict, Optional, Tuple
from pathlib import Path
from dataclasses import dataclass
from contextlib import contextmanager

logger = logging.getLogger(__name__)

@dataclass
class Migration:
    """Represents a database migration"""
    version: str
    description: str
    sql: str
    checksum: str
    applied_at: Optional[datetime] = None
    execution_time_ms: Optional[int] = None

class MigrationManager:
    """Manages database migrations with changelog tracking"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.migrations_table = "schema_migrations"
        self.migrations_dir = Path(__file__).parent / "migrations"
        
        # Ensure migrations directory exists
        self.migrations_dir.mkdir(exist_ok=True)
        
        # Initialize migrations
        self._init_migrations()
    
    def _init_migrations(self):
        """Initialize the migrations system"""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                # Create migrations tracking table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS schema_migrations (
                        version TEXT PRIMARY KEY,
                        description TEXT NOT NULL,
                        sql TEXT NOT NULL,
                        checksum TEXT NOT NULL,
                        applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        execution_time_ms INTEGER,
                        success BOOLEAN DEFAULT TRUE,
                        error_message TEXT
                    )
                """)
                
                # Create index for performance
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_migrations_applied_at 
                    ON schema_migrations(applied_at)
                """)
                
                conn.commit()
                logger.info("Migration system initialized")
                
        except Exception as e:
            logger.error(f"Failed to initialize migration system: {e}")
            raise
    
    @contextmanager
    def _get_connection(self):
        """Context manager for database connections"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()
    
    def _calculate_checksum(self, sql: str) -> str:
        """Calculate checksum for SQL migration"""
        import hashlib
        return hashlib.md5(sql.encode('utf-8')).hexdigest()
    
    def _get_migration_files(self) -> List[Path]:
        """Get all migration files sorted by version"""
        migration_files = []
        for file_path in self.migrations_dir.glob("*.sql"):
            if file_path.name.startswith("V") and "_" in file_path.name:
                migration_files.append(file_path)
        
        # Sort by version number
        migration_files.sort(key=lambda x: x.name)
        return migration_files
    
    def _parse_migration_file(self, file_path: Path) -> Migration:
        """Parse a migration file and extract metadata"""
        try:
            # Parse filename: V1.0.0__Initial_schema.sql
            filename = file_path.stem
            parts = filename.split("__", 1)
            
            if len(parts) != 2:
                raise ValueError(f"Invalid migration filename format: {filename}")
            
            version = parts[0][1:]  # Remove 'V' prefix
            description = parts[1].replace("_", " ")
            
            # Read SQL content
            with open(file_path, 'r', encoding='utf-8') as f:
                sql = f.read().strip()
            
            checksum = self._calculate_checksum(sql)
            
            return Migration(
                version=version,
                description=description,
                sql=sql,
                checksum=checksum
            )
            
        except Exception as e:
            logger.error(f"Failed to parse migration file {file_path}: {e}")
            raise
    
    def _get_applied_migrations(self) -> Dict[str, Migration]:
        """Get all applied migrations from database"""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT version, description, sql, checksum, applied_at, execution_time_ms
                    FROM schema_migrations 
                    WHERE success = TRUE
                    ORDER BY version
                """)
                
                applied_migrations = {}
                for row in cursor.fetchall():
                    migration = Migration(
                        version=row['version'],
                        description=row['description'],
                        sql=row['sql'],
                        checksum=row['checksum'],
                        applied_at=datetime.fromisoformat(row['applied_at']),
                        execution_time_ms=row['execution_time_ms']
                    )
                    applied_migrations[migration.version] = migration
                
                return applied_migrations
                
        except Exception as e:
            logger.error(f"Failed to get applied migrations: {e}")
            return {}
    
    def _apply_migration(self, migration: Migration) -> bool:
        """Apply a single migration"""
        start_time = datetime.now()
        
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                # Execute migration SQL
                cursor.executescript(migration.sql)
                
                # Record migration
                execution_time = (datetime.now() - start_time).total_seconds() * 1000
                cursor.execute("""
                    INSERT INTO schema_migrations 
                    (version, description, sql, checksum, applied_at, execution_time_ms, success)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    migration.version,
                    migration.description,
                    migration.sql,
                    migration.checksum,
                    start_time.isoformat(),
                    int(execution_time),
                    True
                ))
                
                conn.commit()
                logger.info(f"Applied migration {migration.version}: {migration.description}")
                return True
                
        except Exception as e:
            # Record failed migration
            try:
                with self._get_connection() as conn:
                    cursor = conn.cursor()
                    execution_time = (datetime.now() - start_time).total_seconds() * 1000
                    cursor.execute("""
                        INSERT INTO schema_migrations 
                        (version, description, sql, checksum, applied_at, execution_time_ms, success, error_message)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        migration.version,
                        migration.description,
                        migration.sql,
                        migration.checksum,
                        start_time.isoformat(),
                        int(execution_time),
                        False,
                        str(e)
                    ))
                    conn.commit()
            except:
                pass
            
            logger.error(f"Failed to apply migration {migration.version}: {e}")
            return False
    
    def _validate_migration(self, migration: Migration, applied_migration: Migration) -> bool:
        """Validate that a migration hasn't been modified since it was applied"""
        if applied_migration.checksum != migration.checksum:
            logger.error(f"Migration {migration.version} has been modified since it was applied")
            return False
        return True
    
    def migrate(self) -> bool:
        """Run all pending migrations"""
        try:
            logger.info("Starting database migration")
            
            # Get all migration files
            migration_files = self._get_migration_files()
            if not migration_files:
                logger.info("No migration files found")
                return True
            
            # Get applied migrations
            applied_migrations = self._get_applied_migrations()
            
            # Parse and validate migrations
            pending_migrations = []
            for file_path in migration_files:
                migration = self._parse_migration_file(file_path)
                
                if migration.version in applied_migrations:
                    # Validate existing migration
                    applied = applied_migrations[migration.version]
                    if not self._validate_migration(migration, applied):
                        return False
                else:
                    # New migration to apply
                    pending_migrations.append(migration)
            
            if not pending_migrations:
                logger.info("Database is up to date")
                return True
            
            # Apply pending migrations
            logger.info(f"Found {len(pending_migrations)} pending migrations")
            for migration in pending_migrations:
                logger.info(f"Applying migration {migration.version}: {migration.description}")
                if not self._apply_migration(migration):
                    return False
            
            logger.info("Database migration completed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Migration failed: {e}")
            return False
    
    def get_migration_status(self) -> Dict[str, any]:
        """Get current migration status"""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                # Get applied migrations count
                cursor.execute("SELECT COUNT(*) FROM schema_migrations WHERE success = TRUE")
                applied_count = cursor.fetchone()[0]
                
                # Get failed migrations count
                cursor.execute("SELECT COUNT(*) FROM schema_migrations WHERE success = FALSE")
                failed_count = cursor.fetchone()[0]
                
                # Get latest migration
                cursor.execute("""
                    SELECT version, description, applied_at 
                    FROM schema_migrations 
                    WHERE success = TRUE 
                    ORDER BY version DESC 
                    LIMIT 1
                """)
                latest_row = cursor.fetchone()
                
                # Get all migration files
                migration_files = self._get_migration_files()
                total_files = len(migration_files)
                
                status = {
                    "applied_migrations": applied_count,
                    "failed_migrations": failed_count,
                    "total_migration_files": total_files,
                    "pending_migrations": total_files - applied_count,
                    "latest_migration": None,
                    "database_version": "0.0.0"
                }
                
                if latest_row:
                    status["latest_migration"] = {
                        "version": latest_row['version'],
                        "description": latest_row['description'],
                        "applied_at": latest_row['applied_at']
                    }
                    status["database_version"] = latest_row['version']
                
                return status
                
        except Exception as e:
            logger.error(f"Failed to get migration status: {e}")
            return {
                "applied_migrations": 0,
                "failed_migrations": 0,
                "total_migration_files": 0,
                "pending_migrations": 0,
                "latest_migration": None,
                "database_version": "0.0.0"
            }
    
    def create_migration(self, version: str, description: str, sql: str) -> bool:
        """Create a new migration file"""
        try:
            # Sanitize description for filename
            safe_description = description.replace(" ", "_").replace("-", "_")
            filename = f"V{version}__{safe_description}.sql"
            file_path = self.migrations_dir / filename
            
            # Check if file already exists
            if file_path.exists():
                logger.error(f"Migration file already exists: {filename}")
                return False
            
            # Write migration file
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(sql)
            
            logger.info(f"Created migration file: {filename}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create migration file: {e}")
            return False

# Global migration manager instances by database path
migration_managers = {}

def initialize_migrations(db_path: str) -> MigrationManager:
    """Initialize the migration system"""
    global migration_managers
    if db_path not in migration_managers:
        migration_managers[db_path] = MigrationManager(db_path)
    return migration_managers[db_path]

def run_migrations(db_path: str) -> bool:
    """Run database migrations"""
    manager = initialize_migrations(db_path)
    return manager.migrate()

def get_migration_status(db_path: str) -> Dict[str, any]:
    """Get migration status"""
    manager = initialize_migrations(db_path)
    return manager.get_migration_status() 