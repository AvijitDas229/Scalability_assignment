import psycopg2
from datetime import datetime
from typing import List, Dict, Optional, Any
from .router import router

class ShardedMessage:
    
    @staticmethod
    def create(sender_id: int, receiver_id: int, content: str) -> int:
        """Store message in the correct shard"""
        shard_id = router.get_shard(sender_id, receiver_id)
        conn = None
        try:
            conn = router.get_connection(shard_id)
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO messages 
                    (sender_id, receiver_id, content, shard_key, timestamp)
                    VALUES (%s, %s, %s, %s, %s)
                    RETURNING id
                    """,
                    (sender_id, receiver_id, content, shard_id, datetime.utcnow())
                )
                message_id = cur.fetchone()[0]
            conn.commit()
            return message_id
        except psycopg2.Error as e:
            if conn:
                conn.rollback()
            raise Exception(f"Message creation failed: {str(e)}")
        finally:
            if conn:
                conn.close()

    @staticmethod
    def get_conversation(sender_id: int, receiver_id: int, 
                        limit: int = 100) -> List[Dict[str, Any]]:
        """Retrieve conversation from both shards if needed"""
        results = []
        # Check both possible shard combinations
        for shard_id in {router.get_shard(sender_id, receiver_id),
                        router.get_shard(receiver_id, sender_id)}:
            conn = None
            try:
                conn = router.get_connection(shard_id)
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        SELECT id, sender_id, receiver_id, content, timestamp
                        FROM messages
                        WHERE (sender_id = %s AND receiver_id = %s)
                        OR (sender_id = %s AND receiver_id = %s)
                        ORDER BY timestamp DESC
                        LIMIT %s
                        """,
                        (sender_id, receiver_id, receiver_id, sender_id, limit)
                    )
                    columns = [desc[0] for desc in cur.description]
                    results.extend(
                        dict(zip(columns, row)) 
                        for row in cur.fetchall()
                    )
            except psycopg2.Error:
                continue
            finally:
                if conn:
                    conn.close()
        
        # Sort merged results by timestamp
        return sorted(results, key=lambda x: x['timestamp'], reverse=True)[:limit]