from flask import Blueprint, jsonify, request
from app.Service.user_service import UserService
from app.Service.auth_service import AuthService
from app.Utils.jwt_utils import token_required

user_blueprint = Blueprint('usuario', __name__)


@user_blueprint.route('/usuario/cadastro', methods=['POST'])
def create_user():
    user_service = UserService()
    usuario_data = request.json

    try:
        resultado = user_service.user_create(usuario_data)
        if not resultado is None:
            return jsonify({"Mensagem": "Usuário criado com sucesso!"}), 201
        
        else:
            return jsonify(resultado), 500 # erro
        
    except Exception as e:
        return jsonify({"erro": str(e)}), 400

        
    
@user_blueprint.route('/usuario/login', methods=['POST'])
def login():
    data = request.json
    if not data or not 'email' in data or not 'senha' in data:
        return jsonify({"error": "Email e senha são obrigatórios"}), 400
    
    auth_service = AuthService()
    token = auth_service.autenticar_usuario(data['email'], data['senha'])


    if not token:
        return jsonify({'erro': "Credenciais inválidas"}), 401
    
    return jsonify({"token": token})
    # Tenho que retornar tbem nome, foto entre outras coisas necessárias



@user_blueprint.route('usuario/logins_protegidos', methods=['GET'])
@token_required
def get_user_protegidas():
    user_service = UserService()
    user = user_service.user_create()
    return jsonify({"userario": user})



# route usuario/atualizar
@user_blueprint.route('/usuario/atualizar', methods=['PUT'])
def update_user(user_id):
    novos_dados = request.json
    reposta = UserService.atualizar_usuario(user_id, novos_dados)
    return jsonify(reposta)

    








