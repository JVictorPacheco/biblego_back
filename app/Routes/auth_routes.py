from flask import Blueprint, request, jsonify
from app.Service.auth_service import AuthService
from app.Service.token_service import TokenService
from werkzeug.exceptions import Unauthorized, BadRequest
from app.Service.user_analytics_service import UserAnalyticsService
from app.Utils.jwt_utils import token_required
import traceback
from app.Service.user_service import UserService


auth_blueprint = Blueprint('auth', __name__)


@auth_blueprint.route('/usuario/login', methods=['POST'])
def login_usuario():
    """
    Autentica um usuário e retorna tokens JWT
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
            access_token:
              type: string
            refresh_token:
              type: string
            token_type:
              type: string
            expires_in:
              type: integer
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

        # 2. Autentica o usuário (agora já retorna ambos os tokens)
        auth_service = AuthService()
        resultado = auth_service.login(
            email=data['email'],
            senha=data['senha']
        )
        
        print(f"[DEBUG] Access token gerado: {resultado['access_token']}")
        print(f"[DEBUG] Refresh token gerado: {resultado['refresh_token']}")

        # 3. Retorna a resposta diretamente
        return jsonify(resultado), 200
        
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
                description: Refresh token (mesmo ou novo)
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
      
      
      
      
      
      
      
      
      
      
      
@auth_blueprint.route('/analytics/login', methods=['GET'])
def analytics_login():
    """
    Retorna estatísticas de login dos usuários
    ---
    tags:
      - Analytics
    responses:
      200:
        description: Estatísticas de login
        schema:
          type: object
          properties:
            total_usuarios:
              type: integer
            usuarios_com_login:
              type: integer
            primeiros_logins_hoje:
              type: integer
            logins_hoje:
              type: integer
            logins_ultima_semana:
              type: integer
            taxa_usuarios_ativos:
              type: number
            taxa_engajamento_semanal:
              type: number
    """
    try:
        # USA O SERVICE AO INVÉS DO REPOSITORY
        analytics_service = UserAnalyticsService()
        stats = analytics_service.obter_estatisticas_login()
        
        return jsonify(stats), 200
            
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        print(f"Erro ao buscar analytics: {traceback.format_exc()}")
        return jsonify({"error": "Erro interno"}), 500



@auth_blueprint.route('/usuario/<int:user_id>/login-info', methods=['GET'])
def info_login_usuario(user_id):
    """
    Retorna informações de login de um usuário específico
    ---
    tags:
      - Usuários
    parameters:
      - in: path
        name: user_id
        required: true
        type: integer
    responses:
      200:
        description: Informações de login do usuário
      404:
        description: Usuário não encontrado
    """
    try:
        # USA O SERVICE AO INVÉS DO REPOSITORY  
        analytics_service = UserAnalyticsService()
        login_info = analytics_service.obter_info_login_usuario(user_id)
        
        return jsonify(login_info), 200
            
    except ValueError as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        print(f"Erro ao buscar info de login: {traceback.format_exc()}")
        return jsonify({"error": "Erro interno"}), 500