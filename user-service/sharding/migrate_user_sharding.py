# migrate_to_shards.py
import psycopg2
from sharding_router import router

def migrate_existing_data():
    # Connect to original database
    source_conn = psycopg2.connect(
        host='postgres',
        port=5432,
        dbname='user_service_db',
        user='chatuser',
        password='avijit123'
    )
    
    with source_conn.cursor() as source_cur:
        source_cur.execute("SELECT * FROM users")
        for user in source_cur.fetchall():
            user_id, username, password = user
            ShardedUser.create(user_id, username, password)

if __name__ == "__main__":
    migrate_existing_data()