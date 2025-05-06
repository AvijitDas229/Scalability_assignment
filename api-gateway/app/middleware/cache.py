from flask import request, make_response
import json
from functools import wraps
from config import Config

def cache_middleware(app):
    @app.before_request
    def check_cache():
        if request.method != 'GET':
            return
            
        cache_key = f"{request.path}:{json.dumps(request.args, sort_keys=True)}"
        cached = app.redis.get(cache_key)
        
        if cached:
            return make_response(cached.decode('utf-8')), 200, {'Content-Type': 'application/json'}
    
    @app.after_request
    def set_cache(response):
        if (request.method == 'GET' and 
            response.status_code == 200 and 
            'no-cache' not in request.headers):
            
            cache_key = f"{request.path}:{json.dumps(request.args, sort_keys=True)}"
            app.redis.setex(cache_key, 300, response.data)  # Cache for 5 minutes
            
        return response
