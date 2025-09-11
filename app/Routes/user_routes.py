from flask import Blueprint, jsonify, request
from werkzeug.exceptions import BadRequest, Unauthorized
from app.Service.user_service import UserService
from app.Service.auth_service import AuthService
from app.Service.token_service import TokenService
from app.Utils.jwt_utils import token_required

import traceback

user_blueprint = Blueprint('usuario', __name__)


@user_blueprint.route('/usuario/cadastro', methods=['POST'])
def criar_usuario():
  
  
    """
    Cria um novo usuário no sistema
    ---
    tags:
      - Usuários
    consumes:
      - application/json
    produces:
      - application/json
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - nome
            - email
            - telefone
            - cidade
            - estado
            - endereco
            - sexo
            - data_nascimento
            - firebase_uid
            - senha
          properties:
            nome:
              type: string
              example: "João Silva"
              description: Nome completo do usuário
            email:
              type: string
              format: email
              example: "joao@email.com"
              description: E-mail válido do usuário
            telefone:
              type: string
              example: "11999999999"
              description: Telefone com DDD
            cidade:
              type: string
              example: "São Paulo"
            estado:
              type: string
              example: "SP"
              maxLength: 2
            endereco:
              type: string
              example: "Rua Exemplo, 123"
            sexo:
              type: string
              enum: ["M", "F", "Outro"]
              example: "M"
            data_nascimento:
              type: string
              format: date
              example: "1990-01-01"
              description: Formato YYYY-MM-DD
            firebase_uid:
              type: string
              example: "abc123xyz456"
              description: ID do usuário no Firebase
            senha:
              type: string
              format: password
              example: "senhaSegura123"
              minLength: 8
    responses:
      201:
        description: Usuário criado com sucesso
        schema:
          type: object
          properties:
            mensagem:
              type: string
              example: "Usuário criado com sucesso!"
            id:
              type: integer
              example: 123
              description: ID do usuário criado
            status:
              type: string
              example: "ativo"
      400:
        description: Dados inválidos ou faltantes
        schema:
          type: object
          properties:
            erro:
              type: string
              example: "Campos obrigatórios faltando: email, senha"
      500:
        description: Erro interno no servidor
        schema:
          type: object
          properties:
            erro:
              type: string
              example: "Falha ao criar usuário no banco de dados"
    """
    
    
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
        # Tratamento específico para erros de banco
        error_msg = str(e)
        if "usuarios_sexo_check" in error_msg:
            return jsonify({"erro": "Valor inválido para sexo. Use 'M' ou 'F'"}), 400
        elif "usuarios_email_key" in error_msg:
            return jsonify({"erro": "Email já cadastrado no sistema"}), 400
        else:
            return jsonify({"erro": "Falha ao criar usuário: " + error_msg}), 500




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
        

    








