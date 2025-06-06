from flask import Blueprint, request, jsonify
from app.Service.auth_service import AuthService
from app.Service.token_service import TokenService
from werkzeug.exceptions import Unauthorized, BadRequest
from app.Utils.jwt_utils import token_required
import traceback
from app.Service.user_service import UserService

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
          
          
        token = TokenService().gerar_token(['email'],['firebase_uid'])
        print(f"[DEBUG] Token gerado: {token}")

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
            return jsonify({"error": "Refresh token é obrigatório"}), 400

          token_service = TokenService()
          new_tokens = token_service.refresh_tokens(data['refresh_token'])

          return jsonify(new_tokens), 200

    except ValueError as e:
          return jsonify({"error": str(e)}), 401
    except Exception as e:
          print(f"[REFRESH CRITICAL] {traceback.format_exc()}")
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
      - BearerAuth: []
    parameters:
      - name: Authorization
        in: header
        description: Token JWT no formato 'Bearer <token>'
        required: true
        type: string
        format: string
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
        description: Token inválido/expirado ou cabeçalho de autorização faltando
    """
    
    
    try:
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith("Bearer "):
            return jsonify({"erro": "Formato inválido"}), 401

        token = auth_header.split()[1]
        payload = TokenService().verificar_token(token)  # Agora com auditoria corrigida
        
        user = UserService().obter_usuario_por_email(payload["email"])
        if not user:
            return jsonify({"erro": "Usuário não encontrado"}), 404

        return jsonify({
            "mensagem": "Acesso autorizado",
            "usuario": user,
            "token_info": {
                "email": payload["email"],
                "expira_em": payload.get("exp")
            }
        }), 200

    except ValueError as e:
        return jsonify({"erro": str(e)}), 401
    except Exception as e:
        return jsonify({"erro": "Erro interno"}), 500