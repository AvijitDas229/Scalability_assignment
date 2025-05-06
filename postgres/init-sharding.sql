-- USERS table
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password VARCHAR(120) NOT NULL,
    shard_key INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_users_shard_key ON users(shard_key);

-- MESSAGES table
CREATE TABLE IF NOT EXISTS messages (
    id SERIAL,
    sender_id INTEGER NOT NULL,
    receiver_id INTEGER NOT NULL,
    content TEXT NOT NULL,
    shard_key INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id, shard_key)
) PARTITION BY LIST(shard_key);

DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_tables WHERE tablename = 'messages_shard0') THEN
        CREATE TABLE messages_shard0 PARTITION OF messages FOR VALUES IN (0);
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_tables WHERE tablename = 'messages_shard1') THEN
        CREATE TABLE messages_shard1 PARTITION OF messages FOR VALUES IN (1);
    END IF;
END $$;



-- For both shard0 and shard1

CREATE TABLE IF NOT EXISTS rooms (
    id SERIAL PRIMARY KEY,
    sender_id INTEGER NOT NULL,
    receiver_id INTEGER NOT NULL,
    content TEXT NOT NULL,
    shard_key INTEGER NOT NULL,  -- This is critical for partitioning
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);



CREATE TABLE IF NOT EXISTS messages (
    id SERIAL PRIMARY KEY,
    sender_id INTEGER NOT NULL,
    receiver_id INTEGER NOT NULL,
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


-- Partition for shard0 (example values)
CREATE TABLE IF NOT EXISTS messages_shard0 PARTITION OF messages
    FOR VALUES FROM (0) TO (500000);

-- Partition for shard1 (example values)
CREATE TABLE IF NOT EXISTS messages_shard1 PARTITION OF messages
    FOR VALUES FROM (500000) TO (1000000);

-- Index after base + partitions exist
CREATE INDEX IF NOT EXISTS idx_messages_shard_key ON messages(shard_key);
