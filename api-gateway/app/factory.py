# api-gateway/app/factory.py

from flask import Flask
from flask_httpauth import HTTPTokenAuth
from redis import Redis
from app.middleware.auth import auth_middleware
from app.middleware.cache import cache_middleware
from app.routes.auth import bp as auth_bp
from app.routes.user import bp as user_bp
from app.routes.chat import bp as chat_bp
from config import Config

auth = HTTPTokenAuth(scheme='Bearer')

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Redis connection
    app.redis = Redis(
        host=app.config['REDIS_HOST'],
        port=app.config['REDIS_PORT'],
        db=app.config['REDIS_DB']
    )

    # Middleware
    auth_middleware(app)
    cache_middleware(app)

    # Register Blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(chat_bp)

    @app.route('/health')
    def health():
        return {"status": "healthy"}, 200

    return app
