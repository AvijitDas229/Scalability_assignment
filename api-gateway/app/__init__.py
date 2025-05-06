from flask import Flask
from flask_httpauth import HTTPTokenAuth
from redis import Redis
from .middleware.auth import auth_middleware
from .middleware.cache import cache_middleware
from .routes.auth import bp as auth_bp
from .routes.user import bp as user_bp
from .routes.chat import bp as chat_bp
from config import Config

auth = HTTPTokenAuth(scheme='Bearer')

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Initialize Redis
    app.redis = Redis(
        host=app.config['REDIS_HOST'],
        port=app.config['REDIS_PORT'],
        db=app.config['REDIS_DB']
    )
    
    # Register middleware
    auth_middleware(app)
    cache_middleware(app)
    
    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(chat_bp)
    
    return app
