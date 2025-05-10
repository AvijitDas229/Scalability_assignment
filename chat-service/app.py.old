from flask import Flask, request, jsonify
from datetime import datetime
from functools import wraps
import jwt
import os
from dotenv import load_dotenv
import psycopg2
from psycopg2 import pool
import time
from psycopg2 import sql

load_dotenv()

app = Flask(__name__)

# Configuration
app.config.update({
    'SECRET_KEY': os.environ.get('SECRET_KEY', 'supersecretkey')
})

# Database Connection Pools
db_pool_shard0 = None
db_pool_shard1 = None

def initialize_db_pools():
    global db_pool_shard0, db_pool_shard1
    max_retries = 5
    retry_delay = 5
    
    for attempt in range(max_retries):
        try:
            db_pool_shard0 = psycopg2.pool.SimpleConnectionPool(
                minconn=1,
                maxconn=10,
                host='postgres-shard0',
                database='shard0',
                user='chatuser',
                password='avijit123'
            )
            
            db_pool_shard1 = psycopg2.pool.SimpleConnectionPool(
                minconn=1,
                maxconn=10,
                host='postgres-shard1',
                database='shard1',
                user='chatuser',
                password='avijit123'
            )
            
            # Test connections
            conn0 = db_pool_shard0.getconn()
            conn1 = db_pool_shard1.getconn()
            with conn0.cursor() as cur:
                cur.execute("SELECT 1")
            with conn1.cursor() as cur:
                cur.execute("SELECT 1")
            db_pool_shard0.putconn(conn0)
            db_pool_shard1.putconn(conn1)
            return True
            
        except Exception as e:
            print(f"Connection attempt {attempt + 1} failed: {str(e)}")
            if attempt < max_retries - 1:
                time.sleep(retry_delay)
                continue
            raise

# Initialize pools when app starts

def initialize_database():
    max_retries = 5
    retry_delay = 5
    
    for attempt in range(max_retries):
        try:
            for pool in [db_pool_shard0, db_pool_shard1]:
                conn = pool.getconn()
                try:
                    with conn.cursor() as cur:
                        # Create rooms table
                        cur.execute("""
                            CREATE TABLE IF NOT EXISTS rooms (
                                id SERIAL PRIMARY KEY,
                                name VARCHAR(100) NOT NULL,
                                description TEXT,
                                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                            )
                        """)
                        
                        # Create messages table
                        cur.execute("""
                            CREATE TABLE IF NOT EXISTS messages (
                                id SERIAL PRIMARY KEY,
                                sender_id INTEGER NOT NULL,
                                receiver_id INTEGER NOT NULL,
                                content TEXT NOT NULL,
                                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                            )
                        """)
                        conn.commit()
                finally:
                    pool.putconn(conn)
            print("Database tables initialized successfully")
            return
        except Exception as e:
            print(f"Initialization attempt {attempt + 1} failed: {str(e)}")
            if attempt < max_retries - 1:
                time.sleep(retry_delay)
                continue
            raise

def verify_database_schema():
    max_retries = 5
    retry_delay = 5
    
    for attempt in range(max_retries):
        try:
            for shard_id, pool in [(0, db_pool_shard0), (1, db_pool_shard1)]:
                conn = pool.getconn()
                try:
                    with conn.cursor() as cur:
                        # Check if table exists and has correct schema
                        cur.execute("""
                            SELECT column_name, data_type 
                            FROM information_schema.columns 
                            WHERE table_name = 'messages'
                        """)
                        columns = {row[0] for row in cur.fetchall()}
                        required_columns = {'id', 'sender_id', 'receiver_id', 'content', 'shard_key', 'created_at'}
                        if not required_columns.issubset(columns):
                            raise Exception(f"Shard {shard_id} missing required columns")
                finally:
                    pool.putconn(conn)
            return True
        except Exception as e:
            print(f"Schema verification attempt {attempt + 1} failed: {str(e)}")
            if attempt < max_retries - 1:
                time.sleep(retry_delay)
                continue
            raise Exception("Database schema verification failed")

initialize_db_pools()
initialize_database()
verify_database_schema()


@app.route('/health')
def health():
    try:
        conn0 = db_pool_shard0.getconn()
        conn1 = db_pool_shard1.getconn()
        
        with conn0.cursor() as cur:
            cur.execute("SELECT 1")
        with conn1.cursor() as cur:
            cur.execute("SELECT 1")
            
        return jsonify({
            "status": "healthy",
            "shard0": "connected",
            "shard1": "connected"
        }), 200
        
    except Exception as e:
        return jsonify({
            "status": "unhealthy",
            "error": str(e)
        }), 500
        
    finally:
        if 'conn0' in locals():
            db_pool_shard0.putconn(conn0)
        if 'conn1' in locals():
            db_pool_shard1.putconn(conn1)

@app.route('/rooms', methods=['POST'])
def create_room():
    try:
        data = request.get_json()
        
        # Store room in both shards for redundancy
        for pool in [db_pool_shard0, db_pool_shard1]:
            conn = pool.getconn()
            try:
                with conn.cursor() as cur:
                    cur.execute(
                        "INSERT INTO rooms (name, description) VALUES (%s, %s) RETURNING id",
                        (data['name'], data['description'])
                    )
                    room_id = cur.fetchone()[0]
                    conn.commit()
            finally:
                pool.putconn(conn)
                
        return jsonify({
            "message": "Room created successfully",
            "room_id": room_id
        }), 201
        
    except Exception as e:
        return jsonify({
            "error": "Room creation failed",
            "details": str(e)
        }), 400

@app.route('/messages', methods=['POST'])
def send_message():
    data = request.get_json()
    try:
        # Calculate shard key (0 or 1)
        shard_key = (data['sender_id'] + data['receiver_id']) % 2
        shard_pool = db_pool_shard0 if shard_key == 0 else db_pool_shard1
        
        conn = shard_pool.getconn()
        with conn.cursor() as cur:
            cur.execute(
                """INSERT INTO messages 
                (sender_id, receiver_id, content, shard_key) 
                VALUES (%s, %s, %s, %s) RETURNING id""",
                (data['sender_id'], data['receiver_id'], 
                 data['content'], shard_key)
            )
            message_id = cur.fetchone()[0]
            conn.commit()
            
        return jsonify({
            "message": "Message sent successfully",
            "message_id": message_id,
            "shard": f"shard{shard_key}"
        }), 201
        
    except Exception as e:
        return jsonify({
            "error": "Message sending failed",
            "details": str(e)
        }), 400
    finally:
        if 'conn' in locals():
            shard_pool.putconn(conn)

@app.route('/messages/<int:other_user_id>', methods=['GET'])
def get_conversation(other_user_id):
    sender_id = request.args.get('sender_id')
    if not sender_id:
        return jsonify({"error": "sender_id parameter is required"}), 400
    
    try:
        messages = []
        # We need to check both possible shards since conversations span shards
        for shard_key in [0, 1]:
            shard_pool = db_pool_shard0 if shard_key == 0 else db_pool_shard1
            conn = shard_pool.getconn()
            try:
                with conn.cursor() as cur:
                    cur.execute("""
                        SELECT id, sender_id, receiver_id, content, created_at
                        FROM messages
                        WHERE (sender_id = %s AND receiver_id = %s)
                           OR (sender_id = %s AND receiver_id = %s)
                        ORDER BY created_at
                        LIMIT 100
                        """,
                        (sender_id, other_user_id, other_user_id, sender_id)
                    )
                    for row in cur.fetchall():
                        messages.append({
                            "id": row[0],
                            "sender_id": row[1],
                            "receiver_id": row[2],
                            "content": row[3],
                            "timestamp": row[4].isoformat()
                        })
            finally:
                shard_pool.putconn(conn)
        
        # Sort messages chronologically
        messages.sort(key=lambda x: x['timestamp'])
        return jsonify(messages)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)