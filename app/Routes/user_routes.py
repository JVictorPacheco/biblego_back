from flask import Blueprint, jsonify, request, make_response
from app.Service.user_service import UserService
from app.Service.auth_service import AuthService
from app.Utils.jwt_utils import token_required

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
        resultado = user_service.user_create(usuario_data)
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
        

    # email, senha, nome, data_nascimento, sexo, cidade, endereço, telefone, estado
    


@user_blueprint.route('/usuario/login', methods=['POST'])
def login():
    data = request.json
    response = None
    if not data or not 'email' in data or not 'senha' in data:
        response = jsonify({"error": "Email e senha são obrigatórios"}), 400
    
    auth_service = AuthService()
    token = auth_service.autenticar_usuario(data['email'], data['senha'])


    if not token:
        response = jsonify({'erro': "Credenciais inválidas"}), 401
    
    response = jsonify({"token": token})
    # Tenho que retornar tbem nome, foto entre outras coisas necessárias

    response = make_response((response))
    response.headers['Content-Type'] = 'application/json'
    return response



@user_blueprint.route('/usuario/logins_protegidos', methods=['GET'])
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

    








