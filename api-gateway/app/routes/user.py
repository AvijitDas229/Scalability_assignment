from flask import Blueprint
from app.services.user_client import UserClient

bp = Blueprint('user', __name__, url_prefix='/user')

@bp.route('/<user_id>', methods=['GET'])
def get_user(user_id):
    return UserClient.get_user(user_id)
