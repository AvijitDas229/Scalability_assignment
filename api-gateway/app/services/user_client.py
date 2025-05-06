import requests
from config import Config
from requests.exceptions import RequestException
from flask import jsonify, request

class UserClient:
    @staticmethod
    def get_user(user_id):
        try:
            response = requests.get(
                f"{Config.USER_SERVICE_URL}/users/{user_id}",
                headers={'Authorization': request.headers.get('Authorization')},
                timeout=Config.SERVICE_TIMEOUT
            )
            return response.json(), response.status_code
        except RequestException as e:
            return jsonify({'error': f'User service unavailable: {str(e)}'}), 503
