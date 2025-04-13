from flask import Blueprint, jsonify, request, make_response
from werkzeug.exceptions import BadRequest, Unauthorized
from app.Service.user_service import UserService
from app.Service.auth_service import AuthService
from app.Utils.jwt_utils import token_required
from app.Repository.usuario_repository import UsuarioRepository
import bcrypt
import traceback

user_blueprint = Blueprint('usuario', __name__)


@user_blueprint.route('/usuario/cadastro', methods=['POST'])
def create_user():
    user_service = UserService()
    usuario_data = request.json
    
    if not usuario_data:
        return jsonify({"erro": "Dados do usuário não fornecidos"}), 400
    
    try:
        resultado = user_service.criar_usuario(usuario_data)
        
        # Caso de sucesso (resultado é None)
        if resultado is None:
            return jsonify({
                "mensagem": "Usuário criado com sucesso!",
                "detalhes": {
                    "email": usuario_data['email'],
                    "nome": usuario_data.get('nome', ''),
                    "status": "Ativo"
                }
            }), 201
        
        # Caso de erro (resultado é uma tupla com erro)
        if isinstance(resultado, tuple) and len(resultado) == 2:
            return jsonify({
                "mensagem": "Erro ao cadastrar usuário",
                "erro": resultado[0]["erro"]
            }), resultado[1]
        
        # Caso inesperado
        return jsonify({
            "mensagem": "Resposta inesperada do servidor"
        }), 500
        
    except Exception as e:
        return jsonify({
            "mensagem": "Erro ao processar requisição",
            "erro": str(e)
        }), 500
    


@user_blueprint.route('/usuario/login', methods=['POST'])
def login():
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


@user_blueprint.route('/usuario/logins_protegidos', methods=['GET'])
@token_required
def get_user_protegidas():
    user_service = UserService()
    user = user_service.criar_usuario()
    return jsonify({"userario": user})



# route usuario/atualizar
@user_blueprint.route('/usuario/atualizar/<int:user_id>', methods=['PUT'])
def update_user(user_id):
     try:
        
        novos_dados = request.json
        if not novos_dados:
            return jsonify({"Erro": "Nenhum dado fornecido para atualização"}), 400
        
        response = UserService.atualizar_usuario(user_id, novos_dados)
        return jsonify(response[0]), response[1] if isinstance(response, tuple) else 200
    
     except Exception as e:
        return jsonify({"erro": str(e)}), 500
    
    

@user_blueprint.route('/usuario/deletar/<int:user_id>', methods=['DELETE'])
def deletar_usuario(user_id):
    """
    Endpoint para deletar um usuário
    """
    try:
        resultado = UserService.deletar_usuario(user_id)
        return jsonify(resultado[0]), resultado[1]
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

        

    








