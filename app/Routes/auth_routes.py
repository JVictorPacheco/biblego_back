from flask import Blueprint, request, jsonify
from app.Service.auth_service import AuthService
from app.Service.token_service import TokenService
from werkzeug.exceptions import Unauthorized, BadRequest
from app.Utils.jwt_utils import token_required
import traceback

auth_blueprint = Blueprint('auth', __name__)


@auth_blueprint.route('/usuario/login', methods=['POST'])
def login_usuario():
    """
    Autentica um usuário e retorna um token JWT
    ---
    tags:
      - Usuários
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - email
            - senha
          properties:
            email:
              type: string
              example: "usuario@exemplo.com"
            senha:
              type: string
              example: "senha123"
    responses:
      200:
        description: Login bem-sucedido
        schema:
          type: object
          properties:
            token:
              type: string
            usuario:
              type: object
      400:
        description: Dados inválidos
      401:
        description: Credenciais incorretas
    """
    
    
    try:
        data = request.get_json()
        
        # 1. Validação básica do input
        if not data or 'email' not in data or 'senha' not in data:
            raise BadRequest("Email e senha são obrigatórios")

        # 2. Delega toda a lógica para o service
        auth_service = AuthService()
        resultado = auth_service.login(
            email=data['email'],
            senha=data['senha']
        )

        # 3. Formata a resposta
        return jsonify({
            "token": resultado['token'],
            "usuario": resultado['usuario']
        }), 200

    except BadRequest as e:
        return jsonify({"error": str(e)}), 400
    except Unauthorized as e:
        return jsonify({"error": str(e)}), 401
    except Exception as e:
        print(f"ERRO: {traceback.format_exc()}")
        return jsonify({"error": "Erro interno"}), 500
    
    
    
    
@auth_blueprint.route('/auth/refresh', methods=['POST'])
def refresh():
        """
    Renova os tokens de autenticação usando um refresh token válido
    ---
    tags:
      - Autenticação
    summary: Renova access_token e refresh_token
    description: Endpoint para renovar os tokens JWT quando o access_token expira. Requer um refresh_token válido obtido durante o login.
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - refresh_token
          properties:
            refresh_token:
              type: string
              description: Refresh token válido obtido no login
              example: "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
    responses:
      200:
        description: Tokens renovados com sucesso
        schema:
          type: object
          properties:
            access_token:
              type: string
              description: Novo token de acesso (JWT)
            refresh_token:
              type: string
              description: Novo refresh token
            token_type:
              type: string
              example: "bearer"
            expires_in:
              type: integer
              description: Tempo de expiração em segundos
              example: 3600
      400:
        description: Dados de entrada inválidos
        schema:
          type: object
          properties:
            error:
              type: string
              example: "Refresh token é obrigatório"
      401:
        description: Token inválido ou expirado
        schema:
          type: object
          properties:
            error:
              type: string
              example: "Refresh token expirado ou inválido"
    security: []
    """
        try:
            data = request.get_json()
            if not data or 'refresh_token' not in data:
                raise BadRequest("Refresh token é obrigatório")

            auth_service = AuthService()
            new_tokens = auth_service.refresh_tokens(data['refresh_token'])

            return jsonify({
                "access_token": new_tokens['access_token'],
                "refresh_token": new_tokens['refresh_token']
            }), 200

        except BadRequest as e:
            return jsonify({"error": str(e)}), 400
        except Unauthorized as e:
            return jsonify({"error": str(e)}), 401
        except Exception as e:
            return jsonify({"error": "Erro interno"}), 500
        
    
    
    
    
    
@auth_blueprint.route('/usuario/login_protegido', methods=['GET'])
@token_required
def logins_protegidos():
    """
    Acesso a dados protegidos via token JWT
    ---
    tags:
      - Usuários
    security:
      - Bearer: []
    responses:
      200:
        description: Dados do usuário autenticado
        schema:
          type: object
          properties:
            mensagem:
              type: string
            usuario:
              type: object
            token_info:
              type: object
      401:
        description: Token inválido/expirado
    """
    
    
    
    try:
        print("\n[DEBUG] Iniciando rota protegida")  # Log de início
        
        auth_header = request.headers.get('Authorization')
        print(f"[DEBUG] Authorization header: {auth_header}")  # Log do header
        
        if not auth_header:
            return jsonify({"erro": "Cabeçalho de autorização faltando"}), 401
        
        token = auth_header.split()[1]
        print(f"[DEBUG] Token recebido: {token}")  # Log do token
        
        payload = TokenService().verificar_token(token)
        print(f"[DEBUG] Payload decodificado: {payload}")  # Log do payload
        
        if not payload:
            return jsonify({"erro": "Token inválido ou expirado"}), 401
            
        email = payload['email']
        print(f"[DEBUG] Email extraído do token: {email}")  # Log do email
        
        user = UserService().obter_usuario_por_email(email)
        print(f"[DEBUG] Usuário encontrado: {bool(user)}")  # Log se usuário foi encontrado
        
        return jsonify({
            "mensagem": "Acesso autorizado",
            "usuario": user,
            "token_info": {
                "email": email,
                "firebase_uid": payload.get('firebase_uid'),
                "expira_em": payload.get('exp')
            }
        }), 200
        
    except Exception as e:
        print(f"\n[ERRO] Detalhes do erro:")
        print(f"Tipo: {type(e)}")
        print(f"Mensagem: {str(e)}")
        print(traceback.format_exc())
        
        return jsonify({
            "erro": "Erro interno no servidor"
        }), 500