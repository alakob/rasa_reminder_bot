"""
User model with CRUD operations for the users table.
"""
import logging
from typing import Dict, List, Optional, Any, Union
import hashlib

from psycopg2 import sql
from db.connection import get_db_cursor

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def hash_password(password: str) -> str:
    """
    Hash a password using SHA-256.
    
    Args:
        password: Plain text password
        
    Returns:
        Hashed password
    """
    # In a production environment, you should use a more secure method like bcrypt
    # This is a simple implementation for demonstration purposes
    return hashlib.sha256(password.encode()).hexdigest()


def create_user(username: str, email: str, password: str, time_zone: str = 'UTC') -> Dict[str, Any]:
    """
    Create a new user in the database.
    
    Args:
        username: User's username
        email: User's email address
        password: User's password (will be hashed)
        time_zone: User's timezone (default: UTC)
        
    Returns:
        Dictionary containing the created user's information
        
    Raises:
        Exception: If user creation fails
    """
    password_hash = hash_password(password)
    
    try:
        with get_db_cursor() as cursor:
            query = """
            INSERT INTO users (username, email, password_hash, time_zone)
            VALUES (%s, %s, %s, %s)
            RETURNING id, username, email, created_at, updated_at, time_zone
            """
            cursor.execute(query, (username, email, password_hash, time_zone))
            user = cursor.fetchone()
            logger.info(f"Created user with ID: {user['id']}")
            return user
    except Exception as e:
        logger.error(f"Failed to create user: {e}")
        raise


def get_user_by_id(user_id: int) -> Optional[Dict[str, Any]]:
    """
    Get a user by their ID.
    
    Args:
        user_id: User's ID
        
    Returns:
        Dictionary containing user information or None if not found
    """
    try:
        with get_db_cursor() as cursor:
            query = """
            SELECT id, username, email, created_at, updated_at, time_zone
            FROM users
            WHERE id = %s
            """
            cursor.execute(query, (user_id,))
            user = cursor.fetchone()
            return user
    except Exception as e:
        logger.error(f"Failed to get user by ID: {e}")
        raise


def get_user_by_email(email: str) -> Optional[Dict[str, Any]]:
    """
    Get a user by their email address.
    
    Args:
        email: User's email address
        
    Returns:
        Dictionary containing user information or None if not found
    """
    try:
        with get_db_cursor() as cursor:
            query = """
            SELECT id, username, email, created_at, updated_at, time_zone
            FROM users
            WHERE email = %s
            """
            cursor.execute(query, (email,))
            user = cursor.fetchone()
            return user
    except Exception as e:
        logger.error(f"Failed to get user by email: {e}")
        raise


def get_user_by_username(username: str) -> Optional[Dict[str, Any]]:
    """
    Get a user by their username.
    
    Args:
        username: User's username
        
    Returns:
        Dictionary containing user information or None if not found
    """
    try:
        with get_db_cursor() as cursor:
            query = """
            SELECT id, username, email, created_at, updated_at, time_zone
            FROM users
            WHERE username = %s
            """
            cursor.execute(query, (username,))
            user = cursor.fetchone()
            return user
    except Exception as e:
        logger.error(f"Failed to get user by username: {e}")
        raise


def update_user(user_id: int, update_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Update a user's information.
    
    Args:
        user_id: User's ID
        update_data: Dictionary of fields to update (username, email, time_zone)
        
    Returns:
        Updated user information or None if user not found
        
    Raises:
        Exception: If update fails
    """
    # Allowed fields to update
    allowed_fields = {'username', 'email', 'time_zone'}
    
    # Filter out any fields that are not allowed to be updated
    valid_updates = {k: v for k, v in update_data.items() if k in allowed_fields}
    
    if not valid_updates:
        logger.warning("No valid fields to update")
        return get_user_by_id(user_id)
    
    # Build dynamic query
    query_parts = []
    params = []
    
    for field, value in valid_updates.items():
        query_parts.append(f"{field} = %s")
        params.append(value)
    
    # Add updated_at = CURRENT_TIMESTAMP
    query_parts.append("updated_at = CURRENT_TIMESTAMP")
    
    # Add the WHERE condition parameter
    params.append(user_id)
    
    try:
        with get_db_cursor() as cursor:
            query = f"""
            UPDATE users
            SET {', '.join(query_parts)}
            WHERE id = %s
            RETURNING id, username, email, created_at, updated_at, time_zone
            """
            cursor.execute(query, params)
            updated_user = cursor.fetchone()
            
            if updated_user:
                logger.info(f"Updated user with ID: {user_id}")
                return updated_user
            else:
                logger.warning(f"No user found with ID: {user_id}")
                return None
    except Exception as e:
        logger.error(f"Failed to update user: {e}")
        raise


def update_password(user_id: int, new_password: str) -> bool:
    """
    Update a user's password.
    
    Args:
        user_id: User's ID
        new_password: New password (will be hashed)
        
    Returns:
        True if password was updated, False otherwise
        
    Raises:
        Exception: If update fails
    """
    password_hash = hash_password(new_password)
    
    try:
        with get_db_cursor() as cursor:
            query = """
            UPDATE users
            SET password_hash = %s, updated_at = CURRENT_TIMESTAMP
            WHERE id = %s
            RETURNING id
            """
            cursor.execute(query, (password_hash, user_id))
            result = cursor.fetchone()
            
            if result:
                logger.info(f"Updated password for user with ID: {user_id}")
                return True
            else:
                logger.warning(f"No user found with ID: {user_id}")
                return False
    except Exception as e:
        logger.error(f"Failed to update password: {e}")
        raise


def delete_user(user_id: int) -> bool:
    """
    Delete a user by their ID.
    
    Args:
        user_id: User's ID
        
    Returns:
        True if user was deleted, False otherwise
        
    Raises:
        Exception: If deletion fails
    """
    try:
        with get_db_cursor() as cursor:
            query = """
            DELETE FROM users
            WHERE id = %s
            RETURNING id
            """
            cursor.execute(query, (user_id,))
            result = cursor.fetchone()
            
            if result:
                logger.info(f"Deleted user with ID: {user_id}")
                return True
            else:
                logger.warning(f"No user found with ID: {user_id}")
                return False
    except Exception as e:
        logger.error(f"Failed to delete user: {e}")
        raise


def authenticate_user(username_or_email: str, password: str) -> Optional[Dict[str, Any]]:
    """
    Authenticate a user by username/email and password.
    
    Args:
        username_or_email: User's username or email address
        password: User's password
        
    Returns:
        Dictionary containing user information or None if authentication fails
    """
    password_hash = hash_password(password)
    
    try:
        with get_db_cursor() as cursor:
            query = """
            SELECT id, username, email, created_at, updated_at, time_zone
            FROM users
            WHERE (username = %s OR email = %s) AND password_hash = %s
            """
            cursor.execute(query, (username_or_email, username_or_email, password_hash))
            user = cursor.fetchone()
            
            if user:
                logger.info(f"User authenticated: {user['username']}")
                return user
            else:
                logger.warning(f"Authentication failed for: {username_or_email}")
                return None
    except Exception as e:
        logger.error(f"Authentication error: {e}")
        raise 