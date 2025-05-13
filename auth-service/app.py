from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
import datetime
from functools import wraps
import requests
import os
import time
from sqlalchemy.exc import OperationalError

# Initialize extensions
db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://chatuser:avijit123@postgres:5432/auth_service_db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key')
    
    db.init_app(app)

    # Initialize database within app context
    with app.app_context():
        max_retries = 5
        for attempt in range(max_retries):
            try:
                db.create_all()
                break
            except OperationalError:
                if attempt == max_retries - 1:
                    raise
                time.sleep(5)

    # JWT Decorator
    def token_required(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            token = None
            if 'Authorization' in request.headers:
                token = request.headers['Authorization'].split()[1] if 'Bearer' in request.headers['Authorization'] else None
            
            if not token:
                return jsonify({'error': 'Token is missing'}), 401
                
            try:
                data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
                current_user = User.query.get(data['user_id'])
            except:
                return jsonify({'error': 'Token is invalid'}), 401
                
            return f(current_user, *args, **kwargs)
        return decorated

    # Routes
    @app.route('/register', methods=['POST'])
    def register():
        data = request.get_json()
        # ... [rest of your route code]

    @app.route('/login', methods=['POST'])
    def login():
        data = request.get_json()
        # ... [rest of your route code]

    @app.route('/health', methods=['GET'])
    def health():
        return jsonify({"status": "healthy"}), 200

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5000)