import psycopg2
from functools import lru_cache

class MessageShardingRouter:
    def __init__(self):
        self.shards = {
            0: {
                'host': 'postgres-shard0',
                'port': 5432,
                'dbname': 'shard0',
                'user': 'chatuser',
                'password': 'avijit123'
            },
            1: {
                'host': 'postgres-shard1',
                'port': 5432,
                'dbname': 'shard1',
                'user': 'chatuser',
                'password': 'avijit123'
            }
        }
    
    @lru_cache(maxsize=1000)
    def get_shard(self, sender_id: int, receiver_id: int) -> int:
        """Determine shard based on both sender and receiver"""
        return (sender_id + receiver_id) % len(self.shards)
    
    def get_connection(self, shard_id: int):
        """Get connection to specific shard"""
        config = self.shards[shard_id]
        return psycopg2.connect(
            host=config['host'],
            port=config['port'],
            dbname=config['dbname'],
            user=config['user'],
            password=config['password']
        )

router = MessageShardingRouter()