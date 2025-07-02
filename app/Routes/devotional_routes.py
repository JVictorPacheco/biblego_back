from flask import Blueprint, current_app, request, jsonify
from werkzeug.exceptions import BadRequest
from app.Service.devocional_service import DevocionalService
from app.Utils.jwt_utils import token_required
import traceback
from datetime import date, datetime
from werkzeug.exceptions import NotFound, Unauthorized
from app.Service.auth_service import AuthService


devotional_blueprint = Blueprint('devotional', __name__)


# SOLUÇÃO RECOMENDADA: Route simples sem user_id obrigatório
@devotional_blueprint.route('/devocionais/admin', methods=['POST'])
def criar_devocional_admin():
    """
    Cria um novo devocional como administrador (user_id fixo)
    ---
    tags:
      - Devocionais Internos/Admin
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - title
            - main_verse
            - verse_reference
            - book_id
            - chapter
            - verse
            - content
            - application
            - prayer
            - author
            - publish_date
            - tags
          properties:
            title:
              type: string
              example: "Casa Sobre a Rocha"
            main_verse:
              type: string
              example: "Todo aquele, pois, que escuta estas minhas palavras..."
            verse_reference:
              type: string
              example: "Mateus 7:24"
            book_id:
              type: integer
              example: 40
            chapter:
              type: integer
              example: 7
            verse:
              type: integer
              example: 24
            content:
              type: string
              example: "Jesus conclui o Sermão do Monte..."
            application:
              type: string
              example: "Examine os fundamentos da sua vida..."
            prayer:
              type: string
              example: "Senhor Jesus, ajuda-me a ser não apenas ouvinte..."
            author:
              type: string
              example: "Pastora Carla Pereira"
            publish_date:
              type: string
              format: date
              example: "2025-07-10"
            tags:
              type: string
              example: "fundamento, obediência, sabedoria"
    responses:
      201:
        description: Devocional criado com sucesso
      400:
        description: Dados inválidos
      500:
        description: Erro interno do servidor
    """
    try:
        # 1. DEBUG - verificar se request tem dados
        print(f"[DEBUG ADMIN] Content-Type: {request.content_type}")
        print(f"[DEBUG ADMIN] Request is_json: {request.is_json}")
        
        # 2. Obter dados JSON
        devocional_data = request.get_json()
        
        if not devocional_data:
            return jsonify({"erro": "Dados JSON são obrigatórios"}), 400
        
        print(f"[DEBUG ADMIN] Campos recebidos: {list(devocional_data.keys())}")
        
        # 3. User ID fixo para administrador/sistema
        ADMIN_USER_ID = 362  # ou qualquer ID que represente o sistema/admin
        print(f"[DEBUG ADMIN] Usando user_id fixo: {ADMIN_USER_ID}")
        
        # 4. Criar devocional
        devotional_service = DevocionalService()
        resultado, status_code = devotional_service.criar_devocional(devocional_data, ADMIN_USER_ID)
        
        print(f"[DEBUG ADMIN] Resultado: {resultado}, Status: {status_code}")
        return jsonify(resultado), status_code
        
    except Exception as e:
        print(f"[DEBUG ADMIN] Erro na route admin: {e}")
        print(f"[DEBUG ADMIN] Traceback: {traceback.format_exc()}")
        return jsonify({"erro": "Erro interno do servidor"}), 500
        


@devotional_blueprint.route('/admin/devocional/<int:devocional_id>/atualizar', methods=['PUT'])
def atualizar_devocional_interno(devocional_id):
    """
    [INTERNO] Atualiza um devocional existente - USO ADMINISTRATIVO
    ---
    tags:
      - Devocionais Internos/Admin
    description: |
      🔧 **ROTA PARA USO INTERNO/ADMINISTRATIVO**
      
      ⚠️ **SEM AUTENTICAÇÃO** - Para desenvolvimento e manutenção  
      
    parameters:
      - in: path
        name: devocional_id
        required: true
        type: integer
        description: ID do devocional a ser atualizado
        example: 123
      - in: query
        name: confirmar
        required: true
        type: string
        description: Digite "SIM" para confirmar a atualização
        example: "SIM"
        enum: ["SIM"]
      - in: body
        name: body
        required: true
        schema:
          type: object
          properties:
            title:
              type: string
              example: "Novo Título"
            main_verse:
              type: string
              example: "Novo versículo"
            verse_reference:
              type: string
              example: "João 3:16"
            book_id:
              type: integer
              example: 43
            chapter:
              type: integer
              example: 3
            verse:
              type: integer
              example: 16
            content:
              type: string
              example: "Novo conteúdo..."
            application:
              type: string
              example: "Nova aplicação..."
            prayer:
              type: string
              example: "Nova oração..."
            author:
              type: string
              example: "Pastor João"
            publish_date:
              type: string
              format: date
              example: "2025-07-15"
            tags:
              type: string
              example: "fé, esperança"
    responses:
      200:
        description: Devocional atualizado com sucesso
      400:
        description: Confirmação necessária ou dados inválidos
      404:
        description: Devocional não encontrado
      500:
        description: Erro interno do servidor
    """
    try:
        from datetime import datetime
        
        print(f"[ADMIN UPDATE] 🔧 Atualização solicitada - ID: {devocional_id}")
        
        # ✅ VERIFICAR CONFIRMAÇÃO
        confirmacao = request.args.get('confirmar', '').upper().strip()
        if confirmacao != 'SIM':
            return jsonify({
                "erro": "Confirmação necessária para atualização",
                "instrucao": "Adicione confirmar=SIM nos Query Parameters"
            }), 400
        
        # ✅ VALIDAR DADOS JSON
        novos_dados = request.get_json()
        if not novos_dados:
            return jsonify({
                "erro": "Dados JSON são obrigatórios",
                "exemplo": {"title": "Novo título", "author": "Novo autor"}
            }), 400
        
        print(f"[ADMIN UPDATE] Campos para atualizar: {list(novos_dados.keys())}")
        
        # ✅ USAR O REPOSITORY DIRETAMENTE (evita o erro do service)
        from app.Repository.devotionals_repository import DevotionalsRepository
        
        # Verificar se o devocional existe
        devocional_existente = DevotionalsRepository.buscar_devocional_por_id(devocional_id)
        if not devocional_existente:
            return jsonify({"erro": "Devocional não encontrado"}), 404
        
        print(f"[ADMIN UPDATE] Devocional encontrado: {devocional_existente.get('title', 'N/A')}")
        
        # Atualizar no repository
        sucesso = DevotionalsRepository.atualizar_devocional(devocional_id, novos_dados)
        
        if not sucesso:
            return jsonify({"erro": "Falha ao atualizar no banco de dados"}), 500
        
        print(f"[ADMIN UPDATE] ✅ Atualização realizada com sucesso")
        
        # ✅ RESPOSTA DE SUCESSO
        return jsonify({
            "mensagem": "Devocional atualizado com sucesso",
            "id": devocional_id,
            "campos_alterados": list(novos_dados.keys()),
            "titulo_anterior": devocional_existente.get('title'),
            "modo": "interno_administrativo",
            "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            "sem_autenticacao": True,
            "via_swagger": True
        }), 200
        
    except Exception as e:
        print(f"[ADMIN UPDATE] ❌ Erro: {e}")
        print(f"[ADMIN UPDATE] Traceback: {traceback.format_exc()}")
        
        return jsonify({
            "erro": "Erro interno na atualização",
            "detalhes": str(e),
            "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            "dica": "Verifique se o ID do devocional existe e os dados estão corretos"
        }), 500


@devotional_blueprint.route('/dev/devocionais/<int:devocional_id>', methods=['DELETE'])
def deletar_devocional_dev(devocional_id):
    """
    🔧 ROTA INTERNA HÍBRIDA - Melhor dos mundos
    
    Comportamento inteligente:
    - DELETE /dev/devocionais/123 → mostra preview
    - DELETE /dev/devocionais/123?force=true → deleta imediatamente
    """
    try:
        print(f"[DEV] 🎯 Solicitação de exclusão: ID {devocional_id}")
        
        # Verificar se é exclusão forçada (pula preview)
        force_delete = request.args.get('force', '').lower() == 'true'
        
        devotional_service = DevocionalService()
        
        # 1. Buscar devocional primeiro (sempre)
        devocional = devotional_service.devocional_repository.buscar_devocional_por_id(devocional_id)
        
        if not devocional:
            return jsonify({"erro": "Devocional não encontrado"}), 404
        
        # 2. Se force=true, deleta imediatamente
        if force_delete:
            print(f"[DEV] ⚡ Exclusão forçada ativada")
            sucesso = devotional_service.devocional_repository.deletar_devocional(devocional_id)
            
            if sucesso:
                print(f"[DEV] ✅ DELETADO: '{devocional['title']}'")
                return jsonify({
                    "mensagem": "🗑️ Devocional deletado com sucesso",
                    "id": devocional_id,
                    "titulo_deletado": devocional['title'],
                    "autor_deletado": devocional['author'],
                    "modo": "exclusao_forcada"
                }), 200
            else:
                return jsonify({"erro": "Falha ao deletar no banco"}), 500
        
        # 3. Caso contrário, mostra preview e instruções
        print(f"[DEV] 👀 Mostrando preview: '{devocional['title']}'")
        return jsonify({
            "💡 PREVIEW": "Este devocional seria deletado:",
            "📋 dados": {
                "id": devocional['id'],
                "titulo": devocional['title'],
                "autor": devocional['author'],
                "data_publicacao": str(devocional['publish_date']),
                "versiculo_referencia": devocional['verse_reference'],
                "tags": devocional['tags']
            },
            "🚀 para_deletar_imediatamente": f"DELETE /dev/devocionais/{devocional_id}?force=true",
            "⚠️ aviso": "Adicione ?force=true para confirmar a exclusão"
        }), 200
        
    except Exception as e:
        print(f"[DEV] ❌ Erro: {e}")
        return jsonify({"erro": f"Erro interno: {str(e)}"}), 500

     

@devotional_blueprint.route('/devocionais/hoje', methods=['GET'])
def devocional_hoje():
    """
    Retorna o devocional do dia atual
    ---
    tags:
      - Devocionais
    responses:
      200:
        description: Devocional do dia
        schema:
          type: object
      404:
        description: Nenhum devocional encontrado para hoje
      500:
        description: Erro interno do servidor 
    """
    """Retorna o devocional do dia atual"""
    try:
        # ✅ APENAS coordenação - delega para Service
        devotional_service = DevocionalService()
        resultado = devotional_service.obter_devocional_do_dia()
        
        # ✅ Responsabilidade do Route: status HTTP
        return jsonify(resultado), 200
        
    except NotFound as e:
        return jsonify({
            "erro": str(e),
            "data_solicitada": date.today().isoformat()
        }), 404
    except Exception as e:
        current_app.logger.error(f"Erro no endpoint: {str(e)}")
        return jsonify({"erro": "Erro interno do servidor"}), 500
      
      
      
@devotional_blueprint.route('/admin/devocional/<int:devocional_id>/deletar', methods=['DELETE'])      
def deletar_devocional(devocional_id):
    """
    Deleta um devocional específico
    ---
    tags:
      - Devocionais Internos/Admin
    security:
      - BearerAuth: []
    parameters:
      - in: path
        name: devocional_id
        required: true
        type: integer
        description: ID do devocional a ser deletado
        example: 123
      - in: query                    # ← ADICIONE ESTE BLOCO!
        name: confirmar              # ← CAMPO QUE VAI APARECER!
        required: true
        type: string
        description: Digite "SIM" para confirmar a deleção
        example: "SIM"
        enum: ["SIM"]   
    responses:
      200:
        description: Devocional deletado com sucesso
        schema:
          type: object
          properties:
            mensagem:
              type: string
              example: "Devocional deletado com sucesso"
            id:
              type: integer
              example: 123
            titulo:
              type: string
              example: "A Fé que Move Montanhas"
            autor:
              type: string
              example: "Pastor João Silva"
            modo:
              type: string
              example: "interno_desenvolvedor"
      400:
        description: ID inválido
        schema:
          type: object
          properties:
            erro:
              type: string
              example: "ID inválido"
      401:
        description: Token inválido ou expirado
        schema:
          type: object
          properties:
            erro:
              type: string
              example: "Token inválido"
      404:
        description: Devocional não encontrado
        schema:
          type: object
          properties:
            erro:
              type: string
              example: "Devocional não encontrado"
      500:
        description: Erro interno no servidor
        schema:
          type: object
          properties:
            erro:
              type: string
              example: "Falha interna"
    """
    try:
        from datetime import datetime
        
        # ✅ SEGURANÇA INTERNA: Confirmação (sem token)
        confirmacao = request.args.get('confirmar', '').upper()
        if confirmacao != 'SIM':
            return jsonify({
                "erro": "Confirmação necessária. Adicione ?confirmar=SIM"
            }), 400
        
        # ✅ SEM AUTENTICAÇÃO - Uso direto
        devotional_service = DevocionalService()
        resultado = devotional_service.deletar_devocional_interno(devocional_id)
        
        # ✅ Metadados administrativos
        if resultado[1] == 200:
            resultado[0]['modo'] = 'interno_administrativo'
            resultado[0]['timestamp'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        return jsonify(resultado[0]), resultado[1]
        
    except Exception as e:
        return jsonify({"erro": f"Falha interna: {str(e)}"}), 500