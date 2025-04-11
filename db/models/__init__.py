"""
Database models for CRUD operations.
"""
from db.models.user import (
    create_user,
    get_user_by_id,
    get_user_by_email,
    get_user_by_username,
    update_user,
    update_password,
    delete_user,
    authenticate_user,
)

from db.models.reminder import (
    create_reminder,
    get_reminder_by_id,
    get_reminders_by_user_id,
    get_upcoming_reminders,
    get_pending_notifications,
    update_reminder,
    mark_reminder_completed,
    mark_notification_sent,
    delete_reminder,
    delete_completed_reminders,
) 