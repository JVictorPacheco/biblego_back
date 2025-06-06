from functools import wraps
from flask import request, jsonify
from app.Service.token_service import TokenService
from app.Core.security_config import SecurityConfig
import jwt



def token_required(f):
    
    @wraps(f)
    def decorated(*args, **kwargs):
        try:
            token = _extrair_token(request)
            payload = TokenService().verificar_token(token)
            request.token_payload = payload
            return f(*args, **kwargs)
            
        except jwt.ExpiredSignatureError:
            return jsonify({"erro": "Token expirado"}), 401
            
        except ValueError as e:
            return jsonify({"erro": str(e)}), 401
            
        except Exception as e:
            print(f"[AUTH ERROR] {str(e)}")
            return jsonify({"erro": "Erro de autenticação"}), 500
            
    return decorated

def _extrair_token(request) -> str:
    """Extrai token do header Authorization com validação rigorosa"""
    auth_header = request.headers.get('Authorization')
    
    if not auth_header:
        raise ValueError("Cabeçalho de autorização ausente")
        
    parts = auth_header.split()
    
    if len(parts) != 2:
        raise ValueError("Formato inválido. Deve ser: Bearer <token>")
        
    if parts[0].lower() != 'bearer':
        raise ValueError("Esquema de autenticação inválido. Use Bearer")
        
    if not parts[1] or len(parts[1]) < 30:  # Validação básica do comprimento
        raise ValueError("Token malformado")
        
    return parts[1]
#     @wraps(f)
#     def decorated(*args, **kwargs):
#         try:
#             token = _extrair_token(request)
#             payload = TokenService().verificar_token(token)
#             request.token_payload = payload
#             return f(*args, **kwargs)
            
#         except ValueError as e:
#             # Erros específicos de token inválido
#             return jsonify({"erro": str(e)}), 401
#         except Exception as e:
#             # Outros erros inesperados
#             return jsonify({"erro": "Erro de autenticação"}), 500
#     return decorated

#     # def decorated(*args, **kwargs):
#     #     token = _extrair_token(request)
#     #     payload = TokenService().verificar_token(token)
#     #     request.token_payload = payload  # Injeta payload na request
#     #     return f(*args, **kwargs)
#     # return decorated

# def _extrair_token(request) -> str:
#     """Extrai token do header Authorization"""
#     auth_header = request.headers.get('Authorization')
#     if not auth_header:
#         raise ValueError("Token de autenticação necessário")

#     parts = auth_header.split()
#     if len(parts) != 2 or parts[0].lower() != 'bearer':
#         raise ValueError("Formato inválido. Use: Bearer <token>")
    
#     return parts[1]
