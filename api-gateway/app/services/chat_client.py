import requests
from config import Config
from requests.exceptions import RequestException
from flask import jsonify, request

class ChatClient:
    @staticmethod
    def send_message(message_data):
        try:
            response = requests.post(
                f"{Config.CHAT_SERVICE_URL}/messages",
                json=message_data,
                headers={'Authorization': request.headers.get('Authorization')},
                timeout=Config.SERVICE_TIMEOUT
            )
            return response.json(), response.status_code
        except RequestException as e:
            return jsonify({'error': f'Chat service unavailable: {str(e)}'}), 503
