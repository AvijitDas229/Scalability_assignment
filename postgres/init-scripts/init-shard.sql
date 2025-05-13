-- For shard0
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password VARCHAR(120) NOT NULL,
    shard_key INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS messages (
    id SERIAL,
    sender_id INTEGER NOT NULL,
    receiver_id INTEGER NOT NULL,
    content TEXT NOT NULL,
    shard_key INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id, shard_key)
) PARTITION BY LIST(shard_key);

CREATE TABLE IF NOT EXISTS messages_shard0 PARTITION OF messages FOR VALUES IN (0);
CREATE INDEX IF NOT EXISTS idx_users_shard_key ON users(shard_key);
CREATE INDEX IF NOT EXISTS idx_messages_shard_key ON messages(shard_key);