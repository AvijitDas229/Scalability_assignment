import requests
from config import Config
from requests.exceptions import RequestException
from flask import jsonify

class AuthClient:
    @staticmethod
    def login(username, password):
        try:
            response = requests.post(
                f"{Config.AUTH_SERVICE_URL}/login",
                json={'username': username, 'password': password},
                timeout=Config.SERVICE_TIMEOUT
            )
            return response.json(), response.status_code
        except RequestException as e:
            return jsonify({'error': f'Auth service unavailable: {str(e)}'}), 503

    @staticmethod
    def register(username, password):
        try:
            response = requests.post(
                f"{Config.AUTH_SERVICE_URL}/register",
                json={'username': username, 'password': password},
                timeout=Config.SERVICE_TIMEOUT
            )
            return response.json(), response.status_code
        except RequestException as e:
            return jsonify({'error': f'Auth service unavailable: {str(e)}'}), 503