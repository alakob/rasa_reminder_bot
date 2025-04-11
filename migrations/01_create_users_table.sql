-- Create users table
-- This table stores user information for authentication and identification

CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    email VARCHAR(100) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    time_zone VARCHAR(50) DEFAULT 'UTC' -- Store user's preferred time zone
);

-- Add indexes for frequent lookup operations
CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);

-- Add comments for documentation
COMMENT ON TABLE users IS 'Stores user authentication and profile data';
COMMENT ON COLUMN users.id IS 'Primary key for user identification';
COMMENT ON COLUMN users.username IS 'Unique username for login';
COMMENT ON COLUMN users.email IS 'Unique email address for account recovery and notifications';
COMMENT ON COLUMN users.password_hash IS 'Hashed password for security (never store plain passwords)';
COMMENT ON COLUMN users.created_at IS 'Timestamp when the user account was created';
COMMENT ON COLUMN users.updated_at IS 'Timestamp when the user account was last updated';
COMMENT ON COLUMN users.time_zone IS 'User preferred time zone for displaying dates and times'; 