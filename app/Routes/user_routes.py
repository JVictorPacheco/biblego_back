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
    print(usuario_data)
    response = None
    try:
        # usuario = request.get_json()
        # print(usuario)
        resultado = user_service.criar_usuario(usuario_data)
        print(resultado)
        if not resultado is None:
            response = jsonify({'Mensagem': "Erro ao cadastrar usuário"}), 500
        else:
            response = jsonify({"Mensagem": "Usuário criado com sucesso!"}), 201 # erro
    except Exception as e:
        response = jsonify({"erro": str(e)}), 400

    response = make_response((response))
    response.headers['Content-Type'] = 'application/json'
    return response
    


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
@user_blueprint.route('/usuario/atualizar', methods=['PUT'])
def update_user(user_id):
    novos_dados = request.json
    reposta = UserService.atualizar_usuario(user_id, novos_dados)
    return jsonify(reposta)

    








