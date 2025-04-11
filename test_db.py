#!/usr/bin/env python
"""
Test script for database connection and operations.
This script tests the database connection, migration application, and basic CRUD operations.
"""
import logging
import random
import string
from datetime import datetime, timedelta

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def generate_random_string(length=10):
    """Generate a random string of fixed length."""
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for _ in range(length))

def test_migrations():
    """Test applying database migrations."""
    from db.migrations import apply_migrations
    
    logger.info("Testing database migrations...")
    applied = apply_migrations()
    
    if applied:
        logger.info(f"Applied migrations: {', '.join(applied)}")
    else:
        logger.info("No new migrations to apply")
    
    return True

def test_user_operations():
    """Test user CRUD operations."""
    from db.models.user import (
        create_user, get_user_by_id, get_user_by_email, 
        update_user, delete_user, authenticate_user
    )
    
    logger.info("Testing user operations...")
    
    # Generate random test data
    username = f"testuser_{generate_random_string(5)}"
    email = f"{username}@example.com"
    password = generate_random_string(12)
    
    # Create user
    logger.info(f"Creating test user: {username}")
    user = create_user(username, email, password)
    user_id = user['id']
    logger.info(f"Created user with ID: {user_id}")
    
    # Get user by ID
    fetched_user = get_user_by_id(user_id)
    assert fetched_user['username'] == username, "Username mismatch"
    logger.info("Successfully fetched user by ID")
    
    # Get user by email
    fetched_user = get_user_by_email(email)
    assert fetched_user['id'] == user_id, "User ID mismatch"
    logger.info("Successfully fetched user by email")
    
    # Update user
    new_username = f"updated_{username}"
    updated_user = update_user(user_id, {'username': new_username})
    assert updated_user['username'] == new_username, "Update username failed"
    logger.info("Successfully updated user")
    
    # Authenticate user
    auth_user = authenticate_user(email, password)
    assert auth_user is not None, "Authentication failed"
    logger.info("Successfully authenticated user")
    
    # Delete user
    delete_result = delete_user(user_id)
    assert delete_result is True, "Delete user failed"
    logger.info("Successfully deleted user")
    
    return True

def test_reminder_operations():
    """Test reminder CRUD operations."""
    from db.models.user import create_user, delete_user
    from db.models.reminder import (
        create_reminder, get_reminder_by_id, get_reminders_by_user_id,
        update_reminder, mark_reminder_completed, delete_reminder
    )
    
    logger.info("Testing reminder operations...")
    
    # Create a test user first
    username = f"reminderuser_{generate_random_string(5)}"
    email = f"{username}@example.com"
    password = generate_random_string(12)
    
    user = create_user(username, email, password)
    user_id = user['id']
    logger.info(f"Created test user with ID: {user_id}")
    
    try:
        # Create reminder
        title = f"Test reminder {generate_random_string(5)}"
        description = "This is a test reminder created by the test script"
        reminder_time = datetime.now() + timedelta(days=1)
        
        logger.info(f"Creating reminder: {title}")
        reminder = create_reminder(user_id, title, reminder_time, description)
        reminder_id = reminder['id']
        logger.info(f"Created reminder with ID: {reminder_id}")
        
        # Get reminder by ID
        fetched_reminder = get_reminder_by_id(reminder_id)
        assert fetched_reminder['title'] == title, "Reminder title mismatch"
        logger.info("Successfully fetched reminder by ID")
        
        # Get reminders by user ID
        reminders = get_reminders_by_user_id(user_id)
        assert len(reminders) >= 1, "Failed to get reminders by user ID"
        logger.info(f"Successfully fetched {len(reminders)} reminders for user")
        
        # Update reminder
        new_title = f"Updated {title}"
        updated_reminder = update_reminder(reminder_id, {'title': new_title})
        assert updated_reminder['title'] == new_title, "Update reminder failed"
        logger.info("Successfully updated reminder")
        
        # Mark reminder as completed
        completed_reminder = mark_reminder_completed(reminder_id)
        assert completed_reminder['is_completed'] is True, "Mark completed failed"
        logger.info("Successfully marked reminder as completed")
        
        # Delete reminder
        delete_result = delete_reminder(reminder_id)
        assert delete_result is True, "Delete reminder failed"
        logger.info("Successfully deleted reminder")
        
        return True
    finally:
        # Clean up: delete the test user
        delete_user(user_id)
        logger.info(f"Cleaned up test user with ID: {user_id}")

def test_connection_pool():
    """Test connection pooling by making multiple connections."""
    from db.connection import DatabaseConnectionPool
    
    logger.info("Testing database connection pool...")
    
    # Initialize pool with a small number of connections
    pool = DatabaseConnectionPool(min_connections=1, max_connections=5)
    
    # Test getting multiple connections
    connections = []
    try:
        for i in range(3):
            conn = pool.get_connection()
            logger.info(f"Got connection {i+1}")
            connections.append(conn)
        
        logger.info("Successfully created multiple connections from pool")
        
        # Return connections to the pool
        for i, conn in enumerate(connections):
            pool.return_connection(conn)
            logger.info(f"Returned connection {i+1} to pool")
        
        logger.info("Successfully returned all connections to pool")
        
        # Close all connections
        pool.close_all()
        logger.info("Successfully closed all connections in pool")
        
        return True
    except Exception as e:
        logger.error(f"Connection pool test failed: {e}")
        # Make sure to return connections to avoid leaking
        for conn in connections:
            try:
                pool.return_connection(conn)
            except:
                pass
        return False

def main():
    """Run all database tests."""
    logger.info("Starting database tests...")
    
    tests = [
        test_migrations,
        test_connection_pool,
        test_user_operations,
        test_reminder_operations,
    ]
    
    results = []
    for test_func in tests:
        try:
            logger.info(f"Running test: {test_func.__name__}")
            result = test_func()
            results.append(result)
            logger.info(f"Test {test_func.__name__}: {'PASSED' if result else 'FAILED'}")
        except Exception as e:
            logger.error(f"Test {test_func.__name__} failed with error: {e}")
            results.append(False)
    
    passed = results.count(True)
    total = len(results)
    
    logger.info(f"Test summary: {passed} of {total} tests passed")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1) 