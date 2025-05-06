import psycopg2
from typing import Optional, Dict, Any, List
from datetime import datetime
from .router import router  # Import the sharding router

class ShardedUser:
    """Model for handling user data with sharding support"""
    
    @staticmethod
    def create(user_id: int, username: str, password: str) -> bool:
        """
        Create a new user across shards
        Args:
            user_id: Unique user identifier
            username: User's username
            password: Hashed password
        Returns:
            bool: True if creation was successful
        """
        shard_id = router.get_shard(user_id)
        conn = None
        try:
            conn = router.get_connection(shard_id)
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO users 
                    (id, username, password, shard_key, created_at) 
                    VALUES (%s, %s, %s, %s, %s)
                    """,
                    (user_id, username, password, shard_id, datetime.utcnow())
                )
            conn.commit()
            return True
        except psycopg2.Error as e:
            if conn:
                conn.rollback()
            raise Exception(f"Failed to create user: {str(e)}")
        finally:
            if conn:
                conn.close()

    @staticmethod
    def get(user_id: int) -> Optional[Dict[str, Any]]:
        """
        Retrieve a user by ID from the correct shard
        Args:
            user_id: User ID to retrieve
        Returns:
            dict: User data or None if not found
        """
        shard_id = router.get_shard(user_id)
        conn = None
        try:
            conn = router.get_connection(shard_id)
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT id, username, created_at 
                    FROM users 
                    WHERE id = %s
                    """,
                    (user_id,)
                )
                if cur.rowcount == 0:
                    return None
                
                columns = [desc[0] for desc in cur.description]
                return dict(zip(columns, cur.fetchone()))
        except psycopg2.Error as e:
            raise Exception(f"Failed to fetch user: {str(e)}")
        finally:
            if conn:
                conn.close()

    @staticmethod
    def update_password(user_id: int, new_password: str) -> bool:
        """
        Update user password in the correct shard
        Args:
            user_id: User ID to update
            new_password: New hashed password
        Returns:
            bool: True if update was successful
        """
        shard_id = router.get_shard(user_id)
        conn = None
        try:
            conn = router.get_connection(shard_id)
            with conn.cursor() as cur:
                cur.execute(
                    """
                    UPDATE users 
                    SET password = %s 
                    WHERE id = %s
                    """,
                    (new_password, user_id)
                )
            conn.commit()
            return cur.rowcount > 0
        except psycopg2.Error as e:
            if conn:
                conn.rollback()
            raise Exception(f"Failed to update password: {str(e)}")
        finally:
            if conn:
                conn.close()

    @staticmethod
    def delete(user_id: int) -> bool:
        """
        Delete a user from the correct shard
        Args:
            user_id: User ID to delete
        Returns:
            bool: True if deletion was successful
        """
        shard_id = router.get_shard(user_id)
        conn = None
        try:
            conn = router.get_connection(shard_id)
            with conn.cursor() as cur:
                cur.execute(
                    """
                    DELETE FROM users 
                    WHERE id = %s
                    """,
                    (user_id,)
                )
            conn.commit()
            return cur.rowcount > 0
        except psycopg2.Error as e:
            if conn:
                conn.rollback()
            raise Exception(f"Failed to delete user: {str(e)}")
        finally:
            if conn:
                conn.close()

    @staticmethod
    def exists(username: str) -> bool:
        """
        Check if username exists across all shards
        Args:
            username: Username to check
        Returns:
            bool: True if username exists
        """
        for shard_id in router.shards:
            conn = None
            try:
                conn = router.get_connection(shard_id)
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        SELECT 1 FROM users 
                        WHERE username = %s 
                        LIMIT 1
                        """,
                        (username,)
                    )
                    if cur.rowcount > 0:
                        return True
            except psycopg2.Error:
                continue
            finally:
                if conn:
                    conn.close()
        return False