"""
Tests for Database Migration System
"""

import pytest
import os
import tempfile
import sqlite3
from pathlib import Path
from datetime import datetime

from src.database import (
    MigrationManager, 
    Migration, 
    initialize_migrations, 
    run_migrations, 
    get_migration_status
)


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
def temp_migrations_dir():
    """Create a temporary migrations directory"""
    with tempfile.TemporaryDirectory() as tmp_dir:
        yield Path(tmp_dir)


@pytest.fixture
def sample_migration_sql():
    """Sample SQL for testing migrations"""
    return """
    -- Test migration
    CREATE TABLE IF NOT EXISTS test_table (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    
    CREATE INDEX IF NOT EXISTS idx_test_name ON test_table(name);
    """


class TestMigration:
    """Test Migration dataclass"""
    
    def test_migration_creation(self):
        """Test creating a Migration instance"""
        migration = Migration(
            version="1.0.0",
            description="Test migration",
            sql="CREATE TABLE test (id INTEGER);",
            checksum="abc123"
        )
        
        assert migration.version == "1.0.0"
        assert migration.description == "Test migration"
        assert migration.sql == "CREATE TABLE test (id INTEGER);"
        assert migration.checksum == "abc123"
        assert migration.applied_at is None
        assert migration.execution_time_ms is None


class TestMigrationManager:
    """Test MigrationManager functionality"""
    
    def test_migration_manager_initialization(self, temp_db_path, temp_migrations_dir):
        """Test MigrationManager initialization"""
        # Create a custom migration manager with temp directory
        manager = MigrationManager.__new__(MigrationManager)
        manager.db_path = temp_db_path
        manager.migrations_table = "schema_migrations"
        manager.migrations_dir = temp_migrations_dir
        
        # Initialize migrations
        manager._init_migrations()
        
        assert os.path.exists(temp_db_path)
        
        # Check that migrations table was created
        with manager._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='schema_migrations'")
            result = cursor.fetchone()
            assert result is not None
    
    def test_calculate_checksum(self, temp_db_path):
        """Test checksum calculation"""
        manager = MigrationManager(temp_db_path)
        
        sql1 = "CREATE TABLE test (id INTEGER);"
        sql2 = "CREATE TABLE test (id INTEGER);"
        sql3 = "CREATE TABLE test (id INTEGER, name TEXT);"
        
        checksum1 = manager._calculate_checksum(sql1)
        checksum2 = manager._calculate_checksum(sql2)
        checksum3 = manager._calculate_checksum(sql3)
        
        assert checksum1 == checksum2
        assert checksum1 != checksum3
        assert len(checksum1) == 32  # MD5 hash length
    
    def test_parse_migration_file(self, temp_db_path, temp_migrations_dir, sample_migration_sql):
        """Test parsing migration files"""
        manager = MigrationManager.__new__(MigrationManager)
        manager.db_path = temp_db_path
        manager.migrations_table = "schema_migrations"
        manager.migrations_dir = temp_migrations_dir
        
        # Create a test migration file
        migration_file = temp_migrations_dir / "V1.0.0__Test_migration.sql"
        with open(migration_file, 'w') as f:
            f.write(sample_migration_sql)
        
        # Parse the migration file
        migration = manager._parse_migration_file(migration_file)
        
        assert migration.version == "1.0.0"
        assert migration.description == "Test migration"
        assert migration.sql == sample_migration_sql.strip()
        assert migration.checksum is not None
    
    def test_parse_invalid_migration_file(self, temp_db_path, temp_migrations_dir):
        """Test parsing invalid migration files"""
        manager = MigrationManager.__new__(MigrationManager)
        manager.db_path = temp_db_path
        manager.migrations_table = "schema_migrations"
        manager.migrations_dir = temp_migrations_dir
        
        # Create invalid migration file
        invalid_file = temp_migrations_dir / "invalid_file.sql"
        with open(invalid_file, 'w') as f:
            f.write("CREATE TABLE test;")
        
        with pytest.raises(ValueError):
            manager._parse_migration_file(invalid_file)
    
    def test_get_migration_files(self, temp_db_path, temp_migrations_dir):
        """Test getting migration files"""
        manager = MigrationManager.__new__(MigrationManager)
        manager.db_path = temp_db_path
        manager.migrations_table = "schema_migrations"
        manager.migrations_dir = temp_migrations_dir
        
        # Create test migration files
        files = [
            "V1.0.0__First_migration.sql",
            "V1.1.0__Second_migration.sql",
            "V2.0.0__Third_migration.sql",
            "invalid_file.sql"
        ]
        
        for filename in files:
            file_path = temp_migrations_dir / filename
            with open(file_path, 'w') as f:
                f.write("CREATE TABLE test;")
        
        migration_files = manager._get_migration_files()
        
        # Should only return valid migration files, sorted by version
        assert len(migration_files) == 3
        assert migration_files[0].name == "V1.0.0__First_migration.sql"
        assert migration_files[1].name == "V1.1.0__Second_migration.sql"
        assert migration_files[2].name == "V2.0.0__Third_migration.sql"
    
    def test_apply_migration(self, temp_db_path, temp_migrations_dir, sample_migration_sql):
        """Test applying a single migration"""
        manager = MigrationManager.__new__(MigrationManager)
        manager.db_path = temp_db_path
        manager.migrations_table = "schema_migrations"
        manager.migrations_dir = temp_migrations_dir
        
        # Initialize migrations table
        manager._init_migrations()
        
        # Create migration
        migration = Migration(
            version="1.0.0",
            description="Test migration",
            sql=sample_migration_sql,
            checksum=manager._calculate_checksum(sample_migration_sql)
        )
        
        # Apply migration
        success = manager._apply_migration(migration)
        assert success is True
        
        # Check that table was created
        with manager._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='test_table'")
            result = cursor.fetchone()
            assert result is not None
            
            # Check that migration was recorded
            cursor.execute("SELECT version FROM schema_migrations WHERE version = ?", ("1.0.0",))
            result = cursor.fetchone()
            assert result is not None
    
    def test_apply_failed_migration(self, temp_db_path, temp_migrations_dir):
        """Test applying a migration that fails"""
        manager = MigrationManager.__new__(MigrationManager)
        manager.db_path = temp_db_path
        manager.migrations_table = "schema_migrations"
        manager.migrations_dir = temp_migrations_dir
        
        # Initialize migrations table
        manager._init_migrations()
        
        # Create migration with invalid SQL
        migration = Migration(
            version="1.0.0",
            description="Failed migration",
            sql="INVALID SQL STATEMENT;",
            checksum=manager._calculate_checksum("INVALID SQL STATEMENT;")
        )
        
        # Apply migration (should fail)
        success = manager._apply_migration(migration)
        assert success is False
        
        # Check that failed migration was recorded
        with manager._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT success FROM schema_migrations WHERE version = ?", ("1.0.0",))
            result = cursor.fetchone()
            assert result is not None
            assert result['success'] == 0  # False
    
    def test_validate_migration(self, temp_db_path):
        """Test migration validation"""
        manager = MigrationManager(temp_db_path)
        
        # Create two migrations with different checksums
        migration1 = Migration(
            version="1.0.0",
            description="Test migration",
            sql="CREATE TABLE test1 (id INTEGER);",
            checksum="abc123"
        )
        
        migration2 = Migration(
            version="1.0.0",
            description="Test migration",
            sql="CREATE TABLE test2 (id INTEGER);",
            checksum="def456"
        )
        
        # Should fail validation (different checksums)
        assert manager._validate_migration(migration1, migration2) is False
        
        # Should pass validation (same checksum)
        assert manager._validate_migration(migration1, migration1) is True
    
    def test_migrate_empty_database(self, temp_db_path, temp_migrations_dir):
        """Test migrating an empty database"""
        manager = MigrationManager.__new__(MigrationManager)
        manager.db_path = temp_db_path
        manager.migrations_table = "schema_migrations"
        manager.migrations_dir = temp_migrations_dir
        
        # Initialize migrations system
        manager._init_migrations()
        
        # Run migrations with no migration files
        success = manager.migrate()
        assert success is True
    
    def test_migrate_with_files(self, temp_db_path, temp_migrations_dir, sample_migration_sql):
        """Test migrating with migration files"""
        manager = MigrationManager.__new__(MigrationManager)
        manager.db_path = temp_db_path
        manager.migrations_table = "schema_migrations"
        manager.migrations_dir = temp_migrations_dir
        
        # Initialize migrations system
        manager._init_migrations()
        
        # Create migration files
        migration1_file = temp_migrations_dir / "V1.0.0__First_migration.sql"
        with open(migration1_file, 'w') as f:
            f.write(sample_migration_sql)
        
        migration2_file = temp_migrations_dir / "V1.1.0__Second_migration.sql"
        with open(migration2_file, 'w') as f:
            f.write("CREATE TABLE test_table2 (id INTEGER);")
        
        # Run migrations
        success = manager.migrate()
        assert success is True
        
        # Check that both tables were created
        with manager._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='test_table'")
            assert cursor.fetchone() is not None
            
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='test_table2'")
            assert cursor.fetchone() is not None
    
    def test_migrate_with_existing_migrations(self, temp_db_path, temp_migrations_dir, sample_migration_sql):
        """Test migrating when some migrations are already applied"""
        manager = MigrationManager.__new__(MigrationManager)
        manager.db_path = temp_db_path
        manager.migrations_table = "schema_migrations"
        manager.migrations_dir = temp_migrations_dir
        
        # Initialize and apply first migration
        manager._init_migrations()
        migration1 = Migration(
            version="1.0.0",
            description="First migration",
            sql=sample_migration_sql,
            checksum=manager._calculate_checksum(sample_migration_sql)
        )
        manager._apply_migration(migration1)
        
        # Create second migration file
        migration2_file = temp_migrations_dir / "V1.1.0__Second_migration.sql"
        with open(migration2_file, 'w') as f:
            f.write("CREATE TABLE test_table2 (id INTEGER);")
        
        # Run migrations (should only apply the second one)
        success = manager.migrate()
        assert success is True
        
        # Check that both tables exist
        with manager._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='test_table'")
            assert cursor.fetchone() is not None
            
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='test_table2'")
            assert cursor.fetchone() is not None
    
    def test_get_migration_status(self, temp_db_path, temp_migrations_dir, sample_migration_sql):
        """Test getting migration status"""
        manager = MigrationManager.__new__(MigrationManager)
        manager.db_path = temp_db_path
        manager.migrations_table = "schema_migrations"
        manager.migrations_dir = temp_migrations_dir
        
        # Initialize migrations system
        manager._init_migrations()
        
        # Create a migration file to match the applied migration
        migration_file = temp_migrations_dir / "V1.0.0__Test_migration.sql"
        with open(migration_file, 'w') as f:
            f.write(sample_migration_sql)
        
        # Apply the migration
        migration = Migration(
            version="1.0.0",
            description="Test migration",
            sql=sample_migration_sql,
            checksum=manager._calculate_checksum(sample_migration_sql)
        )
        manager._apply_migration(migration)
        
        # Get status
        status = manager.get_migration_status()
        
        assert status["applied_migrations"] == 1
        assert status["failed_migrations"] == 0
        assert status["total_migration_files"] == 1  # One file in temp dir
        assert status["pending_migrations"] == 0
        assert status["database_version"] == "1.0.0"
        assert status["latest_migration"]["version"] == "1.0.0"
    
    def test_create_migration(self, temp_db_path, temp_migrations_dir):
        """Test creating a new migration file"""
        manager = MigrationManager.__new__(MigrationManager)
        manager.db_path = temp_db_path
        manager.migrations_table = "schema_migrations"
        manager.migrations_dir = temp_migrations_dir
        
        # Create migration
        sql = "CREATE TABLE test (id INTEGER);"
        success = manager.create_migration("1.0.0", "Test migration", sql)
        
        assert success is True
        
        # Check that file was created
        migration_file = temp_migrations_dir / "V1.0.0__Test_migration.sql"
        assert migration_file.exists()
        
        # Check file content
        with open(migration_file, 'r') as f:
            content = f.read()
            assert content == sql
    
    def test_create_duplicate_migration(self, temp_db_path, temp_migrations_dir):
        """Test creating a migration file that already exists"""
        manager = MigrationManager.__new__(MigrationManager)
        manager.db_path = temp_db_path
        manager.migrations_table = "schema_migrations"
        manager.migrations_dir = temp_migrations_dir
        
        # Create first migration
        sql1 = "CREATE TABLE test1 (id INTEGER);"
        success1 = manager.create_migration("1.0.0", "Test migration", sql1)
        assert success1 is True
        
        # Try to create duplicate migration
        sql2 = "CREATE TABLE test2 (id INTEGER);"
        success2 = manager.create_migration("1.0.0", "Test migration", sql2)
        assert success2 is False


class TestMigrationIntegration:
    """Integration tests for migration system"""
    
    def test_full_migration_workflow(self, temp_db_path, temp_migrations_dir):
        """Test complete migration workflow"""
        # Create migration files
        migration1_file = temp_migrations_dir / "V1.0.0__Create_users_table.sql"
        with open(migration1_file, 'w') as f:
            f.write("""
            CREATE TABLE users (
                id INTEGER PRIMARY KEY,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """)
        
        migration2_file = temp_migrations_dir / "V1.1.0__Add_user_indexes.sql"
        with open(migration2_file, 'w') as f:
            f.write("""
            CREATE INDEX idx_users_username ON users(username);
            CREATE INDEX idx_users_email ON users(email);
            """)
        
        # Create migration manager
        manager = MigrationManager.__new__(MigrationManager)
        manager.db_path = temp_db_path
        manager.migrations_table = "schema_migrations"
        manager.migrations_dir = temp_migrations_dir
        
        # Initialize migrations system
        manager._init_migrations()
        
        # Run migrations
        success = manager.migrate()
        assert success is True
        
        # Verify database state
        with manager._get_connection() as conn:
            cursor = conn.cursor()
            
            # Check tables
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
            assert cursor.fetchone() is not None
            
            # Check indexes
            cursor.execute("SELECT name FROM sqlite_master WHERE type='index' AND name='idx_users_username'")
            assert cursor.fetchone() is not None
            
            cursor.execute("SELECT name FROM sqlite_master WHERE type='index' AND name='idx_users_email'")
            assert cursor.fetchone() is not None
            
            # Check migration records
            cursor.execute("SELECT COUNT(*) FROM schema_migrations WHERE success = TRUE")
            assert cursor.fetchone()[0] == 2
    
    def test_migration_rollback_simulation(self, temp_db_path, temp_migrations_dir):
        """Test simulating a migration rollback scenario"""
        manager = MigrationManager.__new__(MigrationManager)
        manager.db_path = temp_db_path
        manager.migrations_table = "schema_migrations"
        manager.migrations_dir = temp_migrations_dir
        
        # Initialize migrations system
        manager._init_migrations()
        
        # Create and apply initial migration
        migration1_file = temp_migrations_dir / "V1.0.0__Initial_schema.sql"
        with open(migration1_file, 'w') as f:
            f.write("CREATE TABLE test (id INTEGER);")
        
        success = manager.migrate()
        assert success is True
        
        # Simulate modifying the migration file (should fail validation)
        with open(migration1_file, 'w') as f:
            f.write("CREATE TABLE test (id INTEGER, name TEXT);")
        
        # Try to migrate again (should fail validation)
        success = manager.migrate()
        assert success is False


class TestGlobalFunctions:
    """Test global migration functions"""
    
    def test_initialize_migrations(self, temp_db_path):
        """Test initialize_migrations function"""
        manager = initialize_migrations(temp_db_path)
        assert manager is not None
        # The manager should use the provided path, not the default
        assert manager.db_path == temp_db_path
        
        # Should return same instance on second call
        manager2 = initialize_migrations(temp_db_path)
        assert manager is manager2
    
    def test_run_migrations(self, temp_db_path, temp_migrations_dir):
        """Test run_migrations function"""
        # Create migration file
        migration_file = temp_migrations_dir / "V1.0.0__Test_migration.sql"
        with open(migration_file, 'w') as f:
            f.write("CREATE TABLE test (id INTEGER);")
        
        # Mock the migrations directory for the global function
        import database_migrations
        original_init = database_migrations.MigrationManager.__init__
        original_manager = database_migrations.migration_manager
        
        # Reset global manager
        database_migrations.migration_manager = None
        
        def mock_init(self, db_path):
            self.db_path = db_path
            self.migrations_table = "schema_migrations"
            self.migrations_dir = temp_migrations_dir
            self._init_migrations()
        
        database_migrations.MigrationManager.__init__ = mock_init
        
        try:
            success = run_migrations(temp_db_path)
            assert success is True
        finally:
            # Restore original method and manager
            database_migrations.MigrationManager.__init__ = original_init
            database_migrations.migration_manager = original_manager
    
    def test_get_migration_status(self, temp_db_path):
        """Test get_migration_status function"""
        status = get_migration_status(temp_db_path)
        
        assert "applied_migrations" in status
        assert "failed_migrations" in status
        assert "total_migration_files" in status
        assert "pending_migrations" in status
        assert "database_version" in status
        assert "latest_migration" in status 