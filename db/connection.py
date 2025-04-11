"""
PostgreSQL connection utility with connection pooling.
"""
import os
import logging
import contextlib
from typing import Dict, Any, Optional, Generator

import psycopg2
from psycopg2 import pool
from psycopg2.extensions import connection as pg_connection
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()


class DatabaseConnectionPool:
    """
    A connection pool manager for PostgreSQL database connections.
    Implements connection pooling for efficient database access.
    """
    _instance = None
    _pool = None

    def __new__(cls, *args, **kwargs):
        """Singleton pattern to ensure only one pool is created."""
        if cls._instance is None:
            cls._instance = super(DatabaseConnectionPool, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self, min_connections: int = 1, max_connections: int = 10):
        """
        Initialize the connection pool.
        
        Args:
            min_connections: Minimum number of connections to keep in the pool
            max_connections: Maximum number of connections allowed in the pool
        """
        if self._initialized:
            return
            
        self.db_config = self._get_db_config()
        self._create_pool(min_connections, max_connections)
        self._initialized = True
        logger.info(f"Database connection pool initialized with {min_connections}-{max_connections} connections")

    def _get_db_config(self) -> Dict[str, Any]:
        """
        Get database configuration from environment variables.
        
        Returns:
            Dictionary with database connection parameters
        """
        # Default values if not specified
        config = {
            "host": os.getenv("POSTGRES_HOST", "localhost"),
            "port": os.getenv("POSTGRES_PORT", "5432"),
            "database": os.getenv("POSTGRES_DB", "rasa_db"),
            "user": os.getenv("POSTGRES_USER", "rasa"),
            "password": os.getenv("POSTGRES_PASSWORD", "password")
        }
        
        # Check if we have a DB_URL defined (takes precedence if available)
        db_url = os.getenv("DB_URL")
        if db_url:
            config["dsn"] = db_url
            
        return config

    def _create_pool(self, min_connections: int, max_connections: int) -> None:
        """
        Create the connection pool with the specified parameters.
        
        Args:
            min_connections: Minimum number of connections
            max_connections: Maximum number of connections
        """
        try:
            # If we have a DSN, use it instead of individual parameters
            if "dsn" in self.db_config:
                self._pool = pool.ThreadedConnectionPool(
                    min_connections,
                    max_connections,
                    dsn=self.db_config["dsn"]
                )
            else:
                self._pool = pool.ThreadedConnectionPool(
                    min_connections,
                    max_connections,
                    host=self.db_config["host"],
                    port=self.db_config["port"],
                    database=self.db_config["database"],
                    user=self.db_config["user"],
                    password=self.db_config["password"]
                )
            logger.info("Database connection pool created successfully")
        except Exception as e:
            logger.error(f"Failed to create database connection pool: {e}")
            raise

    def get_connection(self) -> pg_connection:
        """
        Get a connection from the pool.
        
        Returns:
            A database connection from the pool
        
        Raises:
            Exception: If no connections are available or an error occurs
        """
        if not self._pool:
            raise Exception("Connection pool not initialized")
            
        try:
            connection = self._pool.getconn()
            return connection
        except Exception as e:
            logger.error(f"Failed to get connection from pool: {e}")
            raise

    def return_connection(self, connection: pg_connection) -> None:
        """
        Return a connection to the pool.
        
        Args:
            connection: The connection to return to the pool
        """
        if not self._pool:
            logger.warning("Attempting to return connection to uninitialized pool")
            return
            
        try:
            self._pool.putconn(connection)
        except Exception as e:
            logger.error(f"Failed to return connection to pool: {e}")
            raise

    def close_all(self) -> None:
        """Close all connections in the pool."""
        if not self._pool:
            logger.warning("Attempting to close uninitialized pool")
            return
            
        try:
            self._pool.closeall()
            logger.info("All database connections closed")
        except Exception as e:
            logger.error(f"Failed to close all connections: {e}")
            raise


@contextlib.contextmanager
def get_db_connection() -> Generator[pg_connection, None, None]:
    """
    Context manager for safe database connection handling.
    
    Yields:
        A database connection that will be automatically returned to the pool
        
    Example:
        ```python
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT * FROM users")
                results = cursor.fetchall()
        ```
    """
    pool_manager = DatabaseConnectionPool()
    connection = None
    
    try:
        connection = pool_manager.get_connection()
        yield connection
    finally:
        if connection:
            pool_manager.return_connection(connection)


@contextlib.contextmanager
def get_db_cursor(cursor_factory: Optional[Any] = RealDictCursor) -> Generator[Any, None, None]:
    """
    Context manager for safe database cursor handling.
    
    Args:
        cursor_factory: The cursor factory to use (default: RealDictCursor for dict-like results)
    
    Yields:
        A database cursor that will be automatically closed
        
    Example:
        ```python
        with get_db_cursor() as cursor:
            cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
            user = cursor.fetchone()
        ```
    """
    with get_db_connection() as connection:
        cursor = None
        try:
            cursor = connection.cursor(cursor_factory=cursor_factory)
            yield cursor
            connection.commit()
        except Exception:
            connection.rollback()
            raise
        finally:
            if cursor:
                cursor.close()


def convert_to_utc(datetime_value, user_timezone: str = 'UTC'):
    """
    Convert a datetime from user timezone to UTC for storage.
    
    Args:
        datetime_value: The datetime value to convert
        user_timezone: The user's timezone (default: UTC)
        
    Returns:
        Datetime in UTC timezone
    """
    # This is a placeholder for a more comprehensive timezone conversion utility
    # In a real implementation, you would use something like pytz or dateutil
    # For now, we'll assume the input is already in UTC
    return datetime_value


def convert_from_utc(datetime_value, user_timezone: str = 'UTC'):
    """
    Convert a datetime from UTC to user timezone for display.
    
    Args:
        datetime_value: The datetime value to convert (from database/UTC)
        user_timezone: The user's timezone (default: UTC)
        
    Returns:
        Datetime in user's timezone
    """
    # This is a placeholder for a more comprehensive timezone conversion utility
    # In a real implementation, you would use something like pytz or dateutil
    return datetime_value 