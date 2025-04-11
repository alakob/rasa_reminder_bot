-- Create reminders table
-- This table stores user reminders with scheduling information

CREATE TABLE IF NOT EXISTS reminders (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    title VARCHAR(100) NOT NULL,
    description TEXT,
    reminder_time TIMESTAMP WITH TIME ZONE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    is_completed BOOLEAN DEFAULT FALSE,
    notification_sent BOOLEAN DEFAULT FALSE,
    
    -- Foreign key constraint to users table
    CONSTRAINT fk_user
        FOREIGN KEY (user_id)
        REFERENCES users(id)
        ON DELETE CASCADE
);

-- Add indexes for frequent lookup operations
CREATE INDEX IF NOT EXISTS idx_reminders_user_id ON reminders(user_id);
CREATE INDEX IF NOT EXISTS idx_reminders_reminder_time ON reminders(reminder_time);
CREATE INDEX IF NOT EXISTS idx_reminders_is_completed ON reminders(is_completed);

-- Add comments for documentation
COMMENT ON TABLE reminders IS 'Stores user task reminders and scheduled notifications';
COMMENT ON COLUMN reminders.id IS 'Primary key for reminder identification';
COMMENT ON COLUMN reminders.user_id IS 'Foreign key to users table identifying the reminder owner';
COMMENT ON COLUMN reminders.title IS 'Short title of the reminder';
COMMENT ON COLUMN reminders.description IS 'Optional detailed description of the reminder';
COMMENT ON COLUMN reminders.reminder_time IS 'When the reminder should be triggered (in UTC)';
COMMENT ON COLUMN reminders.created_at IS 'Timestamp when the reminder was created';
COMMENT ON COLUMN reminders.updated_at IS 'Timestamp when the reminder was last updated';
COMMENT ON COLUMN reminders.is_completed IS 'Flag indicating if the reminder has been marked as complete';
COMMENT ON COLUMN reminders.notification_sent IS 'Flag indicating if notification has been sent for this reminder'; 