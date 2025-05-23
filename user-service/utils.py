import jwt
from flask import request, jsonify
from functools import wraps

SECRET_KEY = 'supersecretkey'  # Must match the key in auth-service

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None

        # Check if Authorization header is present
        if 'Authorization' in request.headers:
            token = request.headers['Authorization'].split(" ")[1]  # Expecting 'Bearer <token>'

        if not token:
            return jsonify({'message': 'Token is missing!'}), 401

        try:
            data = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            current_user_id = data['user_id']
        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'message': 'Invalid token'}), 401

        return f(current_user_id, *args, **kwargs)

    return decorated
