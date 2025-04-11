# Database Schema Design

This document outlines the design decisions for the database schema used in the Rasa PostgreSQL chatbot project.

## Tables Overview

### Users Table

The `users` table stores user authentication and profile information:

- **id**: Primary key for user identification
- **username**: Unique username for login
- **email**: Unique email address for account recovery and notifications
- **password_hash**: Hashed password for security (never store plain passwords)
- **created_at**: Timestamp when the user account was created
- **updated_at**: Timestamp when the user account was last updated
- **time_zone**: User preferred time zone for displaying dates and times

#### Design Decisions

1. **Separate Authentication and Profile Data**: This approach allows us to keep authentication data secure while still providing flexibility for profile information.
2. **Username and Email Uniqueness**: Both fields have uniqueness constraints to prevent duplicates.
3. **Time Zone Storage**: Storing user timezone allows for proper localization of reminders.
4. **Indexing Strategy**: Added indexes on `username` and `email` for frequent lookups.

### Reminders Table

The `reminders` table stores user reminders with scheduling information:

- **id**: Primary key for reminder identification
- **user_id**: Foreign key to users table identifying the reminder owner
- **title**: Short title of the reminder
- **description**: Optional detailed description of the reminder
- **reminder_time**: When the reminder should be triggered (stored in UTC)
- **created_at**: Timestamp when the reminder was created
- **updated_at**: Timestamp when the reminder was last updated
- **is_completed**: Flag indicating if the reminder has been marked as complete
- **notification_sent**: Flag indicating if notification has been sent for this reminder

#### Design Decisions

1. **Foreign Key Relationship**: The `user_id` field establishes a many-to-one relationship with the users table, with cascading deletes to ensure referential integrity.
2. **Timestamp Handling**: All timestamps are stored in UTC format and converted to the user's local timezone when displayed.
3. **Notification State Tracking**: The `notification_sent` flag allows the system to track which reminders have already triggered notifications.
4. **Indexing Strategy**: Added indexes on `user_id`, `reminder_time`, and `is_completed` to optimize common queries.

## Database Interaction

### Connection Pooling

We've implemented connection pooling to efficiently manage database connections, which:

- Reduces the overhead of creating new connections
- Provides better performance under load
- Manages connection lifecycle automatically

### CRUD Operations

All database operations follow a consistent pattern:

- Parameter validation and sanitization
- Error handling with specific exception types
- Transaction support for operations that modify multiple tables
- Timezone conversion between UTC and user's timezone

## Migration Strategy

The database uses SQL migration scripts for version control:

- Numbered migration files (e.g., `01_create_users_table.sql`)
- Tracking table to record applied migrations
- Forward-only migration approach

## Security Considerations

- Password hashing using secure algorithms
- No plaintext passwords stored anywhere
- Parameterized queries to prevent SQL injection
- Proper input validation before database operations
- User-specific data access controls

## Future Expansion

The schema is designed to accommodate future requirements:

- Additional user profile fields can be added to the users table
- Reminder categories or tags could be implemented as a separate table
- Recurring reminders could be supported with additional fields 