import jwt
import os

from functools import wraps
from flask import request, jsonify

from app.constants.http_status_codes import HTTP_400_BAD_REQUEST, HTTP_403_FORBIDDEN


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwagrg):
        
        auth = request.headers.get('Authorization')
        
        if not auth:
            return jsonify({
                "code": HTTP_400_BAD_REQUEST, 
                "name": 'Bad request', 
                "description": "Token is missing!"
            }), HTTP_400_BAD_REQUEST

        try:
            token = auth.split()[1] 
            jwt.decode(token, os.getenv('SECRET_KEY'), algorithms=['HS256'])
        
        except Exception:
            return jsonify({
                "code": HTTP_403_FORBIDDEN, 
                "name": 'Forbidden', 
                "description": "Token is not valid!",
               
            }), HTTP_403_FORBIDDEN
            
        return f(*args, **kwagrg)
    return decorated
