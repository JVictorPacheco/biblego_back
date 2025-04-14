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
def pegar_usario_protegidas():
    try:
        # O token_required já validou o token, mas vamos extrair novamente para exemplo
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return jsonify({"erro": "Cabeçalho de autorização faltando"}), 401
        
        # CORREÇÃO AQUI: Usar split() com parênteses
        parts = auth_header.split()
        if len(parts) != 2 or parts[0].lower() != 'bearer':
            return jsonify({"erro": "Formato de token inválido"}), 401
        
        token = parts[1]
        auth_service = AuthService()
        payload = auth_service.verificar_token(token)
        
        if not payload:
            return jsonify({"erro": "Token inválido ou expirado"}), 401
            
        user_id = payload.get('usuario_id')
        if not user_id:
            return jsonify({"erro": "ID de usuário não encontrado no token"}), 400
        
        user_service = UserService()
        user = user_service.obter_usuario_por_id(user_id)
        
        if not user:
            return jsonify({"erro": "Usuário não encontrado"}), 404
            
        return jsonify({
            "mensagem": "Acesso autorizado",
            "usuario": user,
            "token_info": {
                "user_id": user_id,
                "expira_em": payload.get('exp')
            }
        }), 200
        
    except Exception as e:
        print(f"Erro detalhado: {str(e)}")
        print(traceback.format_exc())
        return jsonify({
            "erro": "Erro interno no servidor",
            "detalhes": str(e)  # Isso ajuda no debug (remova em produção)
        }), 500
    



# route usuario/atualizar
@user_blueprint.route('/usuario/atualizar/<int:user_id>', methods=['PUT'])
def atualizar_usuario(user_id):
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

        

    








