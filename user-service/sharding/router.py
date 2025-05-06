import psycopg2
from functools import lru_cache

class ShardingRouter:
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
    
    @lru_cache(maxsize=100)
    def get_shard(self, key: int) -> int:
        """Determine which shard to use based on shard key"""
        return key % len(self.shards)
    
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

router = ShardingRouter()