from functools import wraps
from flask import request, jsonify
from app.Service.auth_service import AuthService


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Autorization')
        if not token:
            return jsonify({'erro': 'Token de autenticação necessário'}), 401
        

        auth_service = AuthService()
        payload = auth_service.verificar_token(token)
        if not payload:
            return jsonify({'erro': 'Token inválido ou expirado'}), 401
        
        return f(*args, **kwargs)
    return decorated