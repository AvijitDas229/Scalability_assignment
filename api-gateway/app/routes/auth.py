from flask import Blueprint, request, jsonify
from app.services.auth_client import AuthClient

bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    if not data or 'username' not in data or 'password' not in data:
        return jsonify({'error': 'Username and password required'}), 400
    return AuthClient.login(data['username'], data['password'])

@bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    if not data or 'username' not in data or 'password' not in data:
        return jsonify({'error': 'Username and password required'}), 400
    return AuthClient.register(data['username'], data['password'])

@bp.route('/protected', methods=['GET'])
#@token_required  # if you're using a decorator
def protected(current_user):
    return jsonify({'message': f'Welcome {current_user.username}!'})


@bp.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'healthy'})