from functools import wraps
from flask import request, jsonify
from app.Service.token_service import TokenService



def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = _extrair_token(request)
        payload = TokenService().verificar_token(token)
        request.token_payload = payload  # Injeta payload na request
        return f(*args, **kwargs)
    return decorated

def _extrair_token(request) -> str:
    """Extrai token do header Authorization"""
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        raise ValueError("Token de autenticação necessário")

    parts = auth_header.split()
    if len(parts) != 2 or parts[0].lower() != 'bearer':
        raise ValueError("Formato inválido. Use: Bearer <token>")
    
    return parts[1]










# def token_required(f):
#     @wraps(f)
#     def decorated(*args, **kwargs):
#         token = request.headers.get('Authorization')
#         if not token:
#             return jsonify({'erro': 'Token de autenticação necessário'}), 401
        
        
        
#         parts = token.split()
#         if parts[0].lower() != 'bearer' or len(parts) != 2:
#             return jsonify({'Erro':  'Formato de token inválido. Deve ser: Bearer <token>'}), 401
        
#         token_auth = parts[1]
#         auth_service = AuthService()
#         payload = auth_service.verificar_token(token_auth)
#         if not payload:
#             return jsonify({'erro': 'Token inválido ou expirado'}), 401
        
#         return f(*args, **kwargs)
#     return decorated