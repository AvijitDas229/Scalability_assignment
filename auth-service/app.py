from flask import Flask, request, jsonify
import bcrypt
import jwt
import datetime
from functools import wraps
import os
from dotenv import load_dotenv
from sqlalchemy.exc import IntegrityError
from sqlalchemy.exc import OperationalError
import time
from models import db, User

load_dotenv()

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DB_URI")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.getenv("SECRET_KEY", 'your-secret-key-here')
app.config['BCRYPT_LOG_ROUNDS'] = 12  # Configure bcrypt work factor
db.init_app(app)

# JWT Configuration
app.config['JWT_ALGORITHM'] = 'HS256'
app.config['JWT_EXPIRATION_HOURS'] = 24

def hash_password(password):
    """Generate a bcrypt hash for the password"""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt(app.config['BCRYPT_LOG_ROUNDS'])).decode('utf-8')

def check_password(password_hash, password):
    """Verify a password against its hash"""
    try:
        return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))
    except Exception as e:
        app.logger.error(f"Password verification error: {e}")
        return False

@app.route('/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        
        # Validate input
        if not data or not data.get('username') or not data.get('password'):
            return jsonify({"error": "Username and password are required"}), 400
        
        username = data['username'].strip()
        password = data['password'].strip()  # Keeping as plaintext per your request
        
        if len(username) < 4:
            return jsonify({"error": "Username must be at least 4 characters"}), 400
            
        # Check if user exists
        if User.query.filter_by(username=username).first():
            return jsonify({"error": "Username already exists"}), 409
            
        # Create user (plaintext password - FOR TESTING ONLY)
        new_user = User(username=username, password=password)
        db.session.add(new_user)
        db.session.commit()
        
        return jsonify({
            "message": "User registered successfully",
            "user_id": new_user.id
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Registration failed", "details": str(e)}), 500

@app.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        
        # Validate input
        if not data or not data.get('username') or not data.get('password'):
            return jsonify({"error": "Username and password required"}), 400
        
        # Find user
        user = User.query.filter_by(username=data['username']).first()
        
        # Verify user exists and password matches
        if not user:
            app.logger.warning(f"Login attempt for non-existent user: {data['username']}")
            return jsonify({"error": "Invalid credentials"}), 401
            
        # Compare plaintext passwords (TEMPORARY - for testing only)
        if user.password != data['password']:
            app.logger.warning(f"Failed login attempt for user: {data['username']}")
            return jsonify({"error": "Invalid credentials"}), 401
        
        # Create JWT token
        token = jwt.encode({
            'user_id': user.id,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=app.config['JWT_EXPIRATION_HOURS'])
        }, app.config['SECRET_KEY'], algorithm=app.config['JWT_ALGORITHM'])
        
        return jsonify({
            "message": "Login successful",
            "access_token": token,
            "user_id": user.id
        })
        
    except Exception as e:
        app.logger.error(f"Login error: {str(e)}")
        return jsonify({"error": "Login failed", "details": str(e)}), 500
    


@app.route('/health')
def health():
    return jsonify({"status": "healthy"}), 200

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            if auth_header.startswith('Bearer '):
                token = auth_header.split(" ")[1]
                
        if not token:
            return jsonify({'message': 'Token is missing!'}), 401
            
        try:
            data = jwt.decode(
                token, 
                app.config['SECRET_KEY'],
                algorithms=[app.config['JWT_ALGORITHM']]
            )
            current_user = User.query.get(data['user_id'])
            if not current_user:
                raise ValueError("User not found")
        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token has expired'}), 401
        except (jwt.InvalidTokenError, ValueError) as e:
            return jsonify({'message': 'Invalid token', 'error': str(e)}), 401
            
        return f(current_user, *args, **kwargs)
    return decorated

@app.route('/protected')
@token_required
def protected_route(current_user):
    return jsonify({
        'message': f'Welcome {current_user.username}!',
        'user_id': current_user.id
    })

def initialize_database():
    max_retries = 5
    retry_delay = 5
    
    with app.app_context():
        for attempt in range(max_retries):
            try:
                db.create_all()
                print("Database initialized successfully")
                return
            except OperationalError as e:
                print(f"Attempt {attempt + 1} failed: {str(e)}")
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                    continue
                raise

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=5000)