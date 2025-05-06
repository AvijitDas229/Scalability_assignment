import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Redis
    REDIS_HOST = os.getenv('REDIS_HOST', 'redis')
    REDIS_PORT = int(os.getenv('REDIS_PORT', 6379))
    REDIS_DB = int(os.getenv('REDIS_DB', 0))
    
    # Services
    AUTH_SERVICE_URL = os.getenv('AUTH_SERVICE_URL', 'http://auth-service:5000')
    USER_SERVICE_URL = os.getenv('USER_SERVICE_URL', 'http://user-service:5000')
    CHAT_SERVICE_URL = os.getenv('CHAT_SERVICE_URL', 'http://chat-service:5000')
    
    # Security
    SECRET_KEY = os.getenv('SECRET_KEY', 'your-very-secure-secret-key')
    JWT_ALGORITHM = os.getenv('JWT_ALGORITHM', 'HS256')
    
    # Timeouts
    SERVICE_TIMEOUT = int(os.getenv('SERVICE_TIMEOUT', 5))
