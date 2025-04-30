from flask import Blueprint, jsonify, request, make_response
from werkzeug.exceptions import BadRequest, Unauthorized
from app.Service.user_service import UserService
from app.Service.auth_service import AuthService
from app.Service.token_service import TokenService
from app.Utils.jwt_utils import token_required

import traceback

user_blueprint = Blueprint('usuario', __name__)


@user_blueprint.route('/usuario/cadastro', methods=['POST'])
def criar_usuario():
    
    try:
        usuario_data = request.json
        user_service = UserService()
        user_id = user_service.criar_usuario(usuario_data)
        
        return jsonify({
            "mensagem": "Usuário criado com sucesso!",
            "id": user_id,
            "status": "ativo"
        }), 201
        
    except ValueError as e:
        return jsonify({"erro": str(e)}), 400
    except Exception as e:
        # return jsonify({"erro": "Falha ao criar usuário"}), 500
        return jsonify({"erro": e}), 500


@user_blueprint.route('/usuario/login', methods=['POST'])
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




@user_blueprint.route('/usuario/login_protegido', methods=['GET'])
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
    



# route usuario/atualizar
@user_blueprint.route('/usuario/atualizar', methods=['PUT'])
@token_required
def atualizar_usuario():
    """
    Atualiza dados do usuário logado
    ---
    tags:
      - Usuários
    security:
      - BearerAuth: []
    parameters:
      - in: header
        name: Authorization
        required: true
        type: string
        default: "Bearer {seu_token_jwt}"
      - in: body
        name: body
        required: true
        schema:
          type: object
          properties:
            nome:
              type: string
              example: "Novo Nome"
            email:
              type: string
              example: "novo@email.com"
    responses:
      200:
        description: Dados atualizados com sucesso
        schema:
          type: object
          properties:
            mensagem:
              type: string
              example: "Dados atualizados"
      401:
        description: Token inválido ou expirado
      403:
        description: Acesso não autorizado
    """
    
    
    """
    Endpoint para atualizar o usuário logado
    """
    try:
        token = request.headers.get('Authorization').split()[1]
        novos_dados = request.json
        
        
        if not novos_dados:
            return jsonify({"Erro": "Nenhum dado fornecido para atualização"}), 400
        
        
        auth_service = AuthService()
        usuario = auth_service.obter_usuario_por_token(token)
        
        user_service = UserService()
        response = user_service.atualizar_usuario(usuario["id"], novos_dados)
        return jsonify(response[0]), response[1]
        
    except Exception as e:
        return jsonify({"erro": str(e)}), 500
        
    
    




@user_blueprint.route('/usuario/deletar', methods=['DELETE'])
@token_required
def deletar_usuario():
    """
    Deleta o usuário logado
    ---
    tags:
      - Usuários
    security:
      - BearerAuth: []
    parameters:
      - in: header
        name: Authorization
        required: true
        type: string
        default: "Bearer {seu_token_jwt}"
        description: Token JWT obtido no login
    responses:
      200:
        description: Usuário deletado com sucesso
        schema:
          type: object
          properties:
            mensagem:
              type: string
              example: "Usuário deletado com sucesso"
      401:
        description: Token inválido ou expirado
        schema:
          type: object
          properties:
            erro:
              type: string
              example: "Token inválido"
      500:
        description: Erro interno no servidor
        schema:
          type: object
          properties:
            erro:
              type: string
              example: "Falha ao deletar usuário"
    """
    
    
    try:
        # Obtém o token do header
        token = request.headers.get('Authorization').split()[1]
        
        # Obtém o usuário completo a partir do token
        auth_service = AuthService()
        usuario = auth_service.obter_usuario_por_token(token)
        
        # Chama o service para deletar usando o ID do usuário obtido do token
        resultado = UserService.deletar_usuario(usuario["id"])
        
        return jsonify(resultado[0]), resultado[1]
        
    except Exception as e:
        return jsonify({"erro": str(e)}), 500
        

    








