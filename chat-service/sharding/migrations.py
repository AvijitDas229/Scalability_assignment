import psycopg2
from .router import router

def migrate_existing_messages():
    """Migrate existing messages to sharded architecture"""
    source_conn = psycopg2.connect(
        host='postgres',
        port=5432,
        dbname='chat_messages_db',
        user='chatuser',
        password='avijit123'
    )
    
    with source_conn.cursor() as source_cur:
        source_cur.execute("SELECT * FROM messages")
        for message in source_cur.fetchall():
            msg_id, sender_id, receiver_id, content, timestamp = message
            ShardedMessage.create(sender_id, receiver_id, content)

if __name__ == "__main__":
    migrate_existing_messages()