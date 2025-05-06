import time
import os
from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import OperationalError
from sqlalchemy import text
from sharding.router import router
from sharding.models import ShardedUser

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://chatuser:avijit123@postgres:5432/user_service_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)

@app.route('/health')
def health():
    try:
        # Test database connection
        db.session.execute(text('SELECT 1'))
        return {"status": "healthy"}, 200
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}, 500
    

@app.route('/shards/health')
def shard_health():
    status = {}
    for shard_id in router.shards.keys():
        try:
            conn = router.get_connection(shard_id)
            with conn.cursor() as cur:
                cur.execute("SELECT 1")
            status[f'shard_{shard_id}'] = 'healthy'
            conn.close()
        except Exception as e:
            status[f'shard_{shard_id}'] = f'unhealthy: {str(e)}'
    return jsonify(status)



@app.route('/users', methods=['POST'])
def create_user():
    data = request.get_json()
    try:
        user = User(username=data['username'], email=data['email'])
        db.session.add(user)
        db.session.commit()
        return jsonify({"id": user.id}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400

@app.route('/users/<int:user_id>')
def get_user(user_id):
    user = User.query.get(user_id)
    if user:
        return jsonify({"id": user.id, "username": user.username})
    return jsonify({"error": "User not found"}), 404

def initialize_database():
    if os.environ.get("PRIMARY_INSTANCE") == "true":
        print("Creating tables from primary instance...")
        max_retries = 5
        retry_delay = 5
        for attempt in range(max_retries):
            try:
                with app.app_context():
                    db.create_all()
                    print("Database tables created successfully")
                    return True
            except OperationalError as e:
                print(f"Attempt {attempt + 1} failed: {str(e)}")
                if attempt == max_retries - 1:
                    raise
                time.sleep(retry_delay * (attempt + 1))
    else:
        print("Skipping table creation (non-primary instance)")

if __name__ == "__main__":
    initialize_database()
    app.run(host="0.0.0.0", port=5000)