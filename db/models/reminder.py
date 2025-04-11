"""
Reminder model with CRUD operations for the reminders table.
"""
import logging
from typing import Dict, List, Optional, Any, Union
from datetime import datetime

from db.connection import get_db_cursor, convert_to_utc, convert_from_utc

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_reminder(user_id: int, title: str, reminder_time: datetime, description: str = None) -> Dict[str, Any]:
    """
    Create a new reminder for a user.
    
    Args:
        user_id: User ID who the reminder belongs to
        title: Reminder title
        reminder_time: When to remind the user (will be converted to UTC)
        description: Optional detailed description
        
    Returns:
        Dictionary containing the created reminder's information
        
    Raises:
        Exception: If reminder creation fails
    """
    try:
        # Convert reminder time to UTC for storage
        reminder_time_utc = convert_to_utc(reminder_time)
        
        with get_db_cursor() as cursor:
            query = """
            INSERT INTO reminders (user_id, title, description, reminder_time)
            VALUES (%s, %s, %s, %s)
            RETURNING id, user_id, title, description, reminder_time, created_at, updated_at, is_completed, notification_sent
            """
            cursor.execute(query, (user_id, title, description, reminder_time_utc))
            reminder = cursor.fetchone()
            logger.info(f"Created reminder with ID: {reminder['id']} for user: {user_id}")
            return reminder
    except Exception as e:
        logger.error(f"Failed to create reminder: {e}")
        raise


def get_reminder_by_id(reminder_id: int, user_id: Optional[int] = None) -> Optional[Dict[str, Any]]:
    """
    Get a reminder by its ID, optionally filtering by user_id for security.
    
    Args:
        reminder_id: Reminder ID
        user_id: Optional user ID to ensure the reminder belongs to the user
        
    Returns:
        Dictionary containing reminder information or None if not found
    """
    try:
        with get_db_cursor() as cursor:
            query = """
            SELECT id, user_id, title, description, reminder_time, created_at, updated_at, is_completed, notification_sent
            FROM reminders
            WHERE id = %s
            """
            params = [reminder_id]
            
            # If user_id is provided, add it to the query to ensure the reminder belongs to the user
            if user_id is not None:
                query += " AND user_id = %s"
                params.append(user_id)
                
            cursor.execute(query, params)
            reminder = cursor.fetchone()
            
            if reminder:
                # Convert reminder_time from UTC to the user's timezone (would require user's timezone information)
                # This is a placeholder - in a real implementation, you would get the user's timezone and convert
                return reminder
            else:
                logger.warning(f"No reminder found with ID: {reminder_id}")
                return None
    except Exception as e:
        logger.error(f"Failed to get reminder by ID: {e}")
        raise


def get_reminders_by_user_id(user_id: int, include_completed: bool = False, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
    """
    Get all reminders for a user.
    
    Args:
        user_id: User ID
        include_completed: Whether to include completed reminders (default: False)
        limit: Maximum number of reminders to return (default: 100)
        offset: Offset for pagination (default: 0)
        
    Returns:
        List of dictionaries containing reminder information
    """
    try:
        with get_db_cursor() as cursor:
            query = """
            SELECT id, user_id, title, description, reminder_time, created_at, updated_at, is_completed, notification_sent
            FROM reminders
            WHERE user_id = %s
            """
            params = [user_id]
            
            # Add filter for completed reminders if needed
            if not include_completed:
                query += " AND is_completed = FALSE"
                
            # Add order by, limit, and offset
            query += " ORDER BY reminder_time ASC LIMIT %s OFFSET %s"
            params.extend([limit, offset])
            
            cursor.execute(query, params)
            reminders = cursor.fetchall()
            logger.info(f"Retrieved {len(reminders)} reminders for user: {user_id}")
            return reminders
    except Exception as e:
        logger.error(f"Failed to get reminders for user: {e}")
        raise


def get_upcoming_reminders(user_id: int, days: int = 7, limit: int = 10) -> List[Dict[str, Any]]:
    """
    Get upcoming reminders for a user within a specified number of days.
    
    Args:
        user_id: User ID
        days: Number of days to look ahead (default: 7)
        limit: Maximum number of reminders to return (default: 10)
        
    Returns:
        List of dictionaries containing reminder information
    """
    try:
        with get_db_cursor() as cursor:
            query = """
            SELECT id, user_id, title, description, reminder_time, created_at, updated_at, is_completed, notification_sent
            FROM reminders
            WHERE user_id = %s
            AND is_completed = FALSE
            AND reminder_time > CURRENT_TIMESTAMP
            AND reminder_time < (CURRENT_TIMESTAMP + interval '%s days')
            ORDER BY reminder_time ASC
            LIMIT %s
            """
            cursor.execute(query, (user_id, days, limit))
            reminders = cursor.fetchall()
            logger.info(f"Retrieved {len(reminders)} upcoming reminders for user: {user_id}")
            return reminders
    except Exception as e:
        logger.error(f"Failed to get upcoming reminders: {e}")
        raise


def get_pending_notifications() -> List[Dict[str, Any]]:
    """
    Get reminders that are due for notification but haven't been sent yet.
    Used by a notification service to send alerts.
    
    Returns:
        List of dictionaries containing reminder information
    """
    try:
        with get_db_cursor() as cursor:
            query = """
            SELECT r.id, r.user_id, r.title, r.description, r.reminder_time, r.created_at, 
                   r.updated_at, r.is_completed, r.notification_sent, u.email, u.username, u.time_zone
            FROM reminders r
            JOIN users u ON r.user_id = u.id
            WHERE r.is_completed = FALSE
            AND r.notification_sent = FALSE
            AND r.reminder_time <= CURRENT_TIMESTAMP
            ORDER BY r.reminder_time ASC
            """
            cursor.execute(query)
            reminders = cursor.fetchall()
            logger.info(f"Retrieved {len(reminders)} pending notifications")
            return reminders
    except Exception as e:
        logger.error(f"Failed to get pending notifications: {e}")
        raise


def update_reminder(reminder_id: int, update_data: Dict[str, Any], user_id: Optional[int] = None) -> Optional[Dict[str, Any]]:
    """
    Update a reminder's information.
    
    Args:
        reminder_id: Reminder ID
        update_data: Dictionary of fields to update (title, description, reminder_time, is_completed)
        user_id: Optional user ID to ensure the reminder belongs to the user
        
    Returns:
        Updated reminder information or None if reminder not found
        
    Raises:
        Exception: If update fails
    """
    # Allowed fields to update
    allowed_fields = {'title', 'description', 'reminder_time', 'is_completed'}
    
    # Filter out any fields that are not allowed to be updated
    valid_updates = {k: v for k, v in update_data.items() if k in allowed_fields}
    
    if not valid_updates:
        logger.warning("No valid fields to update")
        return get_reminder_by_id(reminder_id, user_id)
    
    # Convert reminder_time to UTC if it's being updated
    if 'reminder_time' in valid_updates:
        valid_updates['reminder_time'] = convert_to_utc(valid_updates['reminder_time'])
    
    # Build dynamic query
    query_parts = []
    params = []
    
    for field, value in valid_updates.items():
        query_parts.append(f"{field} = %s")
        params.append(value)
    
    # Add updated_at = CURRENT_TIMESTAMP
    query_parts.append("updated_at = CURRENT_TIMESTAMP")
    
    # Reset notification_sent if the reminder time is changed or is_completed is changed to False
    if 'reminder_time' in valid_updates or ('is_completed' in valid_updates and not valid_updates['is_completed']):
        query_parts.append("notification_sent = FALSE")
    
    # Add the WHERE condition parameter
    params.append(reminder_id)
    
    # Build the WHERE clause
    where_clause = "id = %s"
    if user_id is not None:
        where_clause += " AND user_id = %s"
        params.append(user_id)
    
    try:
        with get_db_cursor() as cursor:
            query = f"""
            UPDATE reminders
            SET {', '.join(query_parts)}
            WHERE {where_clause}
            RETURNING id, user_id, title, description, reminder_time, created_at, updated_at, is_completed, notification_sent
            """
            cursor.execute(query, params)
            updated_reminder = cursor.fetchone()
            
            if updated_reminder:
                logger.info(f"Updated reminder with ID: {reminder_id}")
                return updated_reminder
            else:
                logger.warning(f"No reminder found with ID: {reminder_id}" + 
                               (f" for user: {user_id}" if user_id else ""))
                return None
    except Exception as e:
        logger.error(f"Failed to update reminder: {e}")
        raise


def mark_reminder_completed(reminder_id: int, is_completed: bool = True, user_id: Optional[int] = None) -> Optional[Dict[str, Any]]:
    """
    Mark a reminder as completed or not completed.
    
    Args:
        reminder_id: Reminder ID
        is_completed: Whether the reminder is completed (default: True)
        user_id: Optional user ID to ensure the reminder belongs to the user
        
    Returns:
        Updated reminder information or None if reminder not found
    """
    return update_reminder(reminder_id, {'is_completed': is_completed}, user_id)


def mark_notification_sent(reminder_id: int) -> bool:
    """
    Mark a reminder's notification as sent.
    
    Args:
        reminder_id: Reminder ID
        
    Returns:
        True if the notification was marked as sent, False otherwise
    """
    try:
        with get_db_cursor() as cursor:
            query = """
            UPDATE reminders
            SET notification_sent = TRUE, updated_at = CURRENT_TIMESTAMP
            WHERE id = %s
            RETURNING id
            """
            cursor.execute(query, (reminder_id,))
            result = cursor.fetchone()
            
            if result:
                logger.info(f"Marked notification as sent for reminder ID: {reminder_id}")
                return True
            else:
                logger.warning(f"No reminder found with ID: {reminder_id}")
                return False
    except Exception as e:
        logger.error(f"Failed to mark notification as sent: {e}")
        raise


def delete_reminder(reminder_id: int, user_id: Optional[int] = None) -> bool:
    """
    Delete a reminder by its ID.
    
    Args:
        reminder_id: Reminder ID
        user_id: Optional user ID to ensure the reminder belongs to the user
        
    Returns:
        True if reminder was deleted, False otherwise
        
    Raises:
        Exception: If deletion fails
    """
    try:
        with get_db_cursor() as cursor:
            query = """
            DELETE FROM reminders
            WHERE id = %s
            """
            params = [reminder_id]
            
            # If user_id is provided, add it to the query to ensure the reminder belongs to the user
            if user_id is not None:
                query += " AND user_id = %s"
                params.append(user_id)
                
            query += " RETURNING id"
            
            cursor.execute(query, params)
            result = cursor.fetchone()
            
            if result:
                logger.info(f"Deleted reminder with ID: {reminder_id}")
                return True
            else:
                logger.warning(f"No reminder found with ID: {reminder_id}" + 
                               (f" for user: {user_id}" if user_id else ""))
                return False
    except Exception as e:
        logger.error(f"Failed to delete reminder: {e}")
        raise


def delete_completed_reminders(user_id: int, days_old: int = 30) -> int:
    """
    Delete completed reminders that are older than a specified number of days.
    
    Args:
        user_id: User ID
        days_old: Delete reminders older than this many days (default: 30)
        
    Returns:
        Number of reminders deleted
        
    Raises:
        Exception: If deletion fails
    """
    try:
        with get_db_cursor() as cursor:
            query = """
            DELETE FROM reminders
            WHERE user_id = %s
            AND is_completed = TRUE
            AND updated_at < (CURRENT_TIMESTAMP - interval '%s days')
            RETURNING id
            """
            cursor.execute(query, (user_id, days_old))
            deleted = cursor.rowcount
            logger.info(f"Deleted {deleted} old completed reminders for user: {user_id}")
            return deleted
    except Exception as e:
        logger.error(f"Failed to delete old reminders: {e}")
        raise 