from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_jwt_extended import create_access_token, JWTManager
import os
from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)

# Database Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DB_URI")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["JWT_SECRET_KEY"] = "supersecretkey"

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
jwt = JWTManager(app)

# User Model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)

# Routes
@app.route("/register", methods=["POST"])
def register():
    data = request.json
    hashed_password = bcrypt.generate_password_hash(data["password"]).decode("utf-8")
    new_user = User(username=data["username"], password=hashed_password)
    db.session.add(new_user)
    db.session.commit()
    return jsonify({"message": "User registered successfully!"}), 201

@app.route("/login", methods=["POST"])
def login():
    data = request.json
    user = User.query.filter_by(username=data["username"]).first()
    if user and bcrypt.check_password_hash(user.password, data["password"]):
        access_token = create_access_token(identity=user.id)
        return jsonify({"access_token": access_token})
    return jsonify({"message": "Invalid credentials"}), 401



@app.route('/messages', methods=['POST'])
def send_message():
    data = request.get_json()
    try:
        # Calculate shard key (simple modulo hashing)
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
            "shard": "shard0" if shard_key == 0 else "shard1"
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
def get_messages(other_user_id):
    try:
        sender_id = request.args.get('sender_id', type=int)
        if not sender_id:
            return jsonify({"error": "sender_id parameter required"}), 400
            
        # Check both possible shards
        messages = []
        for pool in [db_pool_shard0, db_pool_shard1]:
            conn = pool.getconn()
            try:
                with conn.cursor() as cur:
                    cur.execute("""
                        SELECT id, sender_id, receiver_id, content, created_at
                        FROM messages
                        WHERE (sender_id = %s AND receiver_id = %s)
                        OR (sender_id = %s AND receiver_id = %s)
                        ORDER BY created_at DESC
                        LIMIT 100
                        """,
                        (sender_id, other_user_id, other_user_id, sender_id)
                    )
                    messages.extend([{
                        'id': row[0],
                        'sender_id': row[1],
                        'receiver_id': row[2],
                        'content': row[3],
                        'timestamp': row[4].isoformat()
                    } for row in cur.fetchall()])
            finally:
                pool.putconn(conn)
                
        # Sort by timestamp
        messages.sort(key=lambda x: x['timestamp'], reverse=True)
        return jsonify(messages)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(host="0.0.0.0", port=5000, debug=False, use_reloader=False)
