"""
Utility to apply database migrations from SQL scripts.
"""
import os
import logging
from typing import List

from db.connection import get_db_connection

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_migration_files(migrations_dir: str = "migrations") -> List[str]:
    """
    Get a sorted list of SQL migration files from the migrations directory.
    
    Args:
        migrations_dir: Directory containing migration files (default: "migrations")
        
    Returns:
        Sorted list of SQL file paths
    """
    if not os.path.exists(migrations_dir):
        logger.warning(f"Migrations directory '{migrations_dir}' does not exist")
        return []
    
    # Get all .sql files and sort them
    migration_files = [
        os.path.join(migrations_dir, f) 
        for f in os.listdir(migrations_dir) 
        if f.endswith('.sql')
    ]
    migration_files.sort()
    
    return migration_files


def execute_migration_file(file_path: str) -> bool:
    """
    Execute a single SQL migration file.
    
    Args:
        file_path: Path to the SQL file
        
    Returns:
        True if successful, False otherwise
    """
    if not os.path.exists(file_path):
        logger.error(f"Migration file '{file_path}' does not exist")
        return False
    
    try:
        # Read the SQL file
        with open(file_path, 'r') as f:
            sql_content = f.read()
        
        # Execute the SQL
        with get_db_connection() as conn:
            conn.autocommit = True  # Autocommit for DDL statements
            with conn.cursor() as cursor:
                cursor.execute(sql_content)
        
        logger.info(f"Successfully executed migration: {file_path}")
        return True
    except Exception as e:
        logger.error(f"Failed to execute migration {file_path}: {e}")
        return False


def create_migrations_table() -> bool:
    """
    Create the migrations tracking table if it doesn't exist.
    
    Returns:
        True if successful, False otherwise
    """
    try:
        with get_db_connection() as conn:
            conn.autocommit = True
            with conn.cursor() as cursor:
                # Create migrations table to track applied migrations
                cursor.execute("""
                CREATE TABLE IF NOT EXISTS migrations (
                    id SERIAL PRIMARY KEY,
                    filename VARCHAR(255) NOT NULL UNIQUE,
                    applied_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                )
                """)
        logger.info("Created or verified migrations tracking table")
        return True
    except Exception as e:
        logger.error(f"Failed to create migrations table: {e}")
        return False


def is_migration_applied(filename: str) -> bool:
    """
    Check if a migration has already been applied.
    
    Args:
        filename: Migration filename
        
    Returns:
        True if migration has been applied, False otherwise
    """
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    "SELECT 1 FROM migrations WHERE filename = %s",
                    (os.path.basename(filename),)
                )
                return cursor.fetchone() is not None
    except Exception as e:
        logger.error(f"Failed to check if migration is applied: {e}")
        return False


def record_migration(filename: str) -> bool:
    """
    Record that a migration has been applied.
    
    Args:
        filename: Migration filename
        
    Returns:
        True if successful, False otherwise
    """
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    "INSERT INTO migrations (filename) VALUES (%s)",
                    (os.path.basename(filename),)
                )
                conn.commit()
        return True
    except Exception as e:
        logger.error(f"Failed to record migration: {e}")
        return False


def apply_migrations() -> List[str]:
    """
    Apply all pending migrations in order.
    
    Returns:
        List of applied migration filenames
    """
    applied_migrations = []
    
    try:
        # Ensure migrations table exists
        if not create_migrations_table():
            return applied_migrations
        
        # Get migration files
        migration_files = get_migration_files()
        if not migration_files:
            logger.info("No migration files found")
            return applied_migrations
        
        # Apply each migration if not already applied
        for file_path in migration_files:
            filename = os.path.basename(file_path)
            
            if is_migration_applied(filename):
                logger.info(f"Migration already applied: {filename}")
                continue
            
            logger.info(f"Applying migration: {filename}")
            if execute_migration_file(file_path):
                if record_migration(filename):
                    applied_migrations.append(filename)
        
        if applied_migrations:
            logger.info(f"Applied {len(applied_migrations)} migrations")
        else:
            logger.info("No new migrations to apply")
            
        return applied_migrations
    except Exception as e:
        logger.error(f"Migration process failed: {e}")
        return applied_migrations


if __name__ == "__main__":
    # This allows the script to be run directly
    applied = apply_migrations()
    if applied:
        print(f"Applied {len(applied)} migrations: {', '.join(applied)}")
    else:
        print("No migrations applied") 