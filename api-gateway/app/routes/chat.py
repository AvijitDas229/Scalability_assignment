from flask import Blueprint, request, jsonify
from app.services.chat_client import ChatClient

bp = Blueprint('chat', __name__, url_prefix='/chat')

@bp.route('/messages', methods=['POST'])
def send_message():
    data = request.get_json()
    if not data or 'receiver_id' not in data or 'content' not in data:
        return jsonify({'error': 'Receiver ID and content required'}), 400
        
    # Add sender from JWT token
    token = request.headers.get('Authorization').split()[1]
    # In a real app, decode the token properly
    data['sender_id'] = "extracted-from-token"
    
    return ChatClient.send_message(data)
