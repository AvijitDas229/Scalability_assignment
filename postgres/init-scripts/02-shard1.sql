-- postgres/init-scripts/03-shard1-schema.sql
-- Complete initialization script for shard1 database (shard_key = 1)

-- Set permissions (run as superuser first)
DO $$
BEGIN
  IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'chatuser') THEN
    CREATE ROLE chatuser WITH LOGIN PASSWORD 'avijit123';
  END IF;
  
  -- Ensure we have permissions to grant privileges
  IF EXISTS (SELECT FROM pg_roles WHERE rolname = CURRENT_USER AND rolsuper = true) THEN
    EXECUTE 'GRANT ALL ON SCHEMA public TO chatuser';
    EXECUTE 'ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO chatuser';
    EXECUTE 'ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO chatuser';
  END IF;
END $$;

-- Create users table with shard enforcement
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password VARCHAR(120) NOT NULL,
    shard_key INT NOT NULL DEFAULT 1 CHECK (shard_key = 1),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create partitioned messages table
CREATE TABLE IF NOT EXISTS messages (
    id SERIAL,
    sender_id INTEGER NOT NULL,
    receiver_id INTEGER NOT NULL,
    content TEXT NOT NULL,
    shard_key INTEGER NOT NULL DEFAULT 1 CHECK (shard_key = 1),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id, shard_key)
) PARTITION BY LIST(shard_key);

-- Create partition for shard1
CREATE TABLE IF NOT EXISTS messages_shard1 PARTITION OF messages FOR VALUES IN (1);

-- Create rooms table
CREATE TABLE IF NOT EXISTS rooms (
    id SERIAL PRIMARY KEY,
    sender_id INTEGER NOT NULL,
    receiver_id INTEGER NOT NULL,
    content TEXT NOT NULL,
    shard_key INTEGER NOT NULL DEFAULT 1 CHECK (shard_key = 1),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create optimized indexes
CREATE INDEX IF NOT EXISTS idx_users_shard_key ON users(shard_key);
CREATE INDEX IF NOT EXISTS idx_messages_shard_key ON messages(shard_key);
CREATE INDEX IF NOT EXISTS idx_messages_sender ON messages(sender_id) WHERE shard_key = 1;
CREATE INDEX IF NOT EXISTS idx_messages_receiver ON messages(receiver_id) WHERE shard_key = 1;
CREATE INDEX IF NOT EXISTS idx_rooms_shard_key ON rooms(shard_key);

-- Create function for notifications (optional)
CREATE OR REPLACE FUNCTION notify_new_message()
RETURNS TRIGGER AS $$
BEGIN
  PERFORM pg_notify('new_message', json_build_object(
    'id', NEW.id,
    'sender_id', NEW.sender_id,
    'receiver_id', NEW.receiver_id
  )::text);
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create trigger for messages (optional)
DROP TRIGGER IF EXISTS trg_notify_new_message ON messages;
CREATE TRIGGER trg_notify_new_message
AFTER INSERT ON messages
FOR EACH ROW EXECUTE FUNCTION notify_new_message();