from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity
import os
import time
from sqlalchemy.exc import OperationalError

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://chatuser:avijit123@postgres:5432/chat_service_db'
app.config['JWT_SECRET_KEY'] = 'your-very-secure-secret-key'
db = SQLAlchemy(app)
jwt = JWTManager(app)


postgres_host = os.environ.get('POSTGRES_HOST', 'postgres')
postgres_db = os.environ.get('POSTGRES_DB', 'chat_service_db')
postgres_user = os.environ.get('POSTGRES_USER', 'chatuser')
postgres_password = os.environ.get('POSTGRES_PASSWORD', 'avijit123')


# ---------------------- MODELS -----------------------
class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, nullable=False)
    receiver_id = db.Column(db.Integer, nullable=False)
    content = db.Column(db.String(255), nullable=False)

# ---------------------- ROUTES -----------------------
@app.route('/chat/messages', methods=['POST'])
@jwt_required()
def send_message():
    data = request.get_json()
    sender_id = get_jwt_identity()

    try:
        message = Message(
            sender_id=sender_id,
            receiver_id=data['receiver_id'],
            content=data['content']
        )
        db.session.add(message)
        db.session.commit()
        return jsonify({'message': 'Message sent successfully'}), 201
    except Exception as e:
        return jsonify({'error': 'Message sending failed', 'details': str(e)}), 500

@app.route('/chat/messages', methods=['GET'])
@jwt_required()
def get_messages():
    user_id = get_jwt_identity()
    try:
        messages = Message.query.filter(
            (Message.sender_id == user_id) | (Message.receiver_id == user_id)
        ).all()
        return jsonify([
            {
                "id": msg.id,
                "sender_id": msg.sender_id,
                "receiver_id": msg.receiver_id,
                "content": msg.content
            } for msg in messages
        ])
    except Exception as e:
        return jsonify({'error': 'Fetching messages failed', 'details': str(e)}), 500

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'healthy'}), 200


def connect_to_db():
    max_retries = 5
    for attempt in range(max_retries):
        try:
            db.create_all()
            return True
        except OperationalError:
            if attempt == max_retries - 1:
                raise
            time.sleep(5)
    return False

# ---------------------- STARTUP -----------------------
if __name__ == '__main__':
    connect_to_db()
    with app.app_context():
        db.create_all()  # Create tables on startup
    app.run(host='0.0.0.0', port=5000)
