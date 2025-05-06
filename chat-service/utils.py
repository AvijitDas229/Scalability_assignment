import jwt
from flask import request, jsonify
from functools import wraps

# Must match auth-service exactly
SECRET_KEY = 'supersecretkey'  # Must match exactly
ALGORITHM = 'HS256'           # Must match exactly

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(" ")[1]
        
        if not token:
            return jsonify({'message': 'Token is missing!'}), 401

        try:
            data = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            current_user_id = data['user_id']
        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token expired'}), 401
        except jwt.InvalidTokenError as e:
            return jsonify({
                'message': 'Invalid token',
                'error': str(e),
                'debug': f"Used key: {SECRET_KEY}, alg: {ALGORITHM}"
            }), 401
        except Exception as e:
            return jsonify({'message': 'Token verification failed', 'error': str(e)}), 401

        return f(current_user_id, *args, **kwargs)

    return decorated