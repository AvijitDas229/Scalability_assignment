from flask import request, jsonify
import jwt
from functools import wraps
from config import Config

def auth_middleware(app):
    @app.before_request
    def check_auth():
        # Skip auth for these paths
        if request.path in ['/auth/login', '/auth/register', '/health']:
            return
            
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'error': 'Missing or invalid authorization header'}), 401
            
        try:
            token = auth_header.split()[1]
            # Add this verification:
            decoded = jwt.decode(
                token,
                Config.SECRET_KEY,
                algorithms=[Config.JWT_ALGORITHM],
                options={'verify_exp': True}
            )
            # Make user_id available to routes
            request.user_id = decoded['user_id']
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Invalid token'}), 401
        except Exception as e:
            return jsonify({'error': str(e)}), 401