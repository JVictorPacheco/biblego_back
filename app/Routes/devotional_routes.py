from flask import Blueprint, request, jsonify
from werkzeug.exceptions import BadRequest
from app.Service.devotional_service import DevotionalService
from app.Utils.jwt_utils import token_required
import traceback
from datetime import datetime


devotional_blueprint = Blueprint('devotional', __name__)


@devotional_blueprint.route('/devocionais', methods=['POST'])
@token_required
def criar_devocional():
    """
    Cria um novo devocional
    ---
    tags:
      - Devocionais
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
              minLength: 3
              maxLength: 500
              example: "A Paz que Excede Todo Entendimento"
              description: "Título do devocional"
            main_verse:
              type: string
              example: "E a paz de Deus, que excede todo o entendimento, guardará os vossos corações e os vossos sentimentos em Cristo Jesus."
              description: "Versículo principal do devocional"
            verse_reference:
              type: string
              example: "Filipenses 4:7"
              description: "Referência bíblica do versículo"
            book_id:
              type: integer
              minimum: 1
              maximum: 66
              example: 50
              description: "ID do livro bíblico (1-66)"
            chapter:
              type: integer
              minimum: 1
              example: 4
              description: "Capítulo do versículo"
            verse:
              type: integer
              minimum: 1
              example: 7
              description: "Número do versículo"
            content:
              type: string
              minLength: 10
              example: "Em meio às turbulências da vida, Deus nos oferece uma paz que vai além da nossa compreensão humana..."
              description: "Conteúdo principal do devocional"
            application:
              type: string
              minLength: 10
              example: "Hoje, quando você se sentir ansioso ou preocupado, lembre-se de entregar suas cargas ao Senhor..."
              description: "Aplicação prática do devocional"
            prayer:
              type: string
              minLength: 5
              example: "Senhor, obrigado pela paz que só Tu podes dar. Ajuda-me a confiar em Ti em todos os momentos..."
              description: "Oração relacionada ao devocional"
            author:
              type: string
              maxLength: 200
              example: "Pastor João Silva"
              description: "Autor do devocional"
            publish_date:
              type: string
              format: date
              example: "2025-06-10"
              description: "Data de publicação (YYYY-MM-DD)"
            tags:
              type: string
              example: "paz, ansiedade, confiança, fé"
              description: "Tags separadas por vírgula"
    responses:
      201:
        description: Devocional criado com sucesso
        schema:
          type: object
          properties:
            mensagem:
              type: string
              example: "Devocional criado com sucesso"
            id:
              type: integer
              example: 123
            titulo:
              type: string
              example: "A Paz que Excede Todo Entendimento"
      400:
        description: Dados inválidos
        schema:
          type: object
          properties:
            erro:
              type: string
              example: "Campo obrigatório faltando: title"
      401:
        description: Token inválido ou expirado
      409:
        description: Devocional já existe
        schema:
          type: object
          properties:
            erro:
              type: string
              example: "Já existe um devocional com este título e autor"
      500:
        description: Erro interno do servidor
    """
    try:
        devocional_data = request.get_json()
        
        if not devocional_data:
            return jsonify({"erro": "Dados JSON são obrigatórios"}), 400
        
        devotional_service = DevotionalService()
        resultado, status_code = devotional_service.criar_devocional(devocional_data)
        
        return jsonify(resultado), status_code
        
    except BadRequest:
        return jsonify({"erro": "JSON inválido"}), 400
    except Exception as e:
        print(f"Erro ao criar devocional: {traceback.format_exc()}")
        return jsonify({"erro": "Erro interno do servidor"}), 500


@devotional_blueprint.route('/devocionais/<int:devocional_id>', methods=['GET'])
def obter_devocional(devocional_id):
    """
    Obtém um devocional pelo ID
    ---
    tags:
      - Devocionais
    parameters:
      - in: path
        name: devocional_id
        required: true
        type: integer
        description: ID do devocional
    responses:
      200:
        description: Devocional encontrado
        schema:
          type: object
          properties:
            id:
              type: integer
            title:
              type: string
            main_verse:
              type: string
            verse_reference:
              type: string
            book_id:
              type: integer
            chapter:
              type: integer
            verse:
              type: integer
            content:
              type: string
            application:
              type: string
            prayer:
              type: string
            author:
              type: string
            publish_date:
              type: string
              format: date
            tags:
              type: string
      400:
        description: ID inválido
      404:
        description: Devocional não encontrado
      500:
        description: Erro interno do servidor
    """
    try:
        devotional_service = DevotionalService()
        resultado, status_code = devotional_service.obter_devocional_por_id(devocional_id)
        
        return jsonify(resultado), status_code
        
    except Exception as e:
        print(f"Erro ao obter devocional: {traceback.format_exc()}")
        return jsonify({"erro": "Erro interno do servidor"}), 500


@devotional_blueprint.route('/devocionais', methods=['GET'])
def listar_devocionais():
    """
    Lista devocionais com paginação e filtros
    ---
    tags:
      - Devocionais
    parameters:
      - in: query
        name: pagina
        type: integer
        default: 1
        description: Número da página (a partir de 1)
      - in: query
        name: limite
        type: integer
        default: 20
        maximum: 100
        description: Número de itens por página
      - in: query
        name: author
        type: string
        description: Filtrar por autor (busca parcial)
      - in: query
        name: book_id
        type: integer
        description: Filtrar por ID do livro bíblico
      - in: query
        name: chapter
        type: integer
        description: Filtrar por capítulo
      - in: query
        name: tags
        type: string
        description: Filtrar por tags (busca parcial)
      - in: query
        name: start_date
        type: string
        format: date
        description: Data inicial para filtro (YYYY-MM-DD)
      - in: query
        name: end_date
        type: string
        format: date
        description: Data final para filtro (YYYY-MM-DD)
      - in: query
        name: search_text
        type: string
        description: Busca livre no título, conteúdo e aplicação
    responses:
      200:
        description: Lista de devocionais
        schema:
          type: object
          properties:
            devocionais:
              type: array
              items:
                type: object
                properties:
                  id:
                    type: integer
                  title:
                    type: string
                  author:
                    type: string
                  publish_date:
                    type: string
                    format: date
                  verse_reference:
                    type: string
                  tags:
                    type: string
            paginacao:
              type: object
              properties:
                pagina_atual:
                  type: integer
                total_paginas:
                  type: integer
                total_itens:
                  type: integer
                itens_por_pagina:
                  type: integer
                tem_proxima:
                  type: boolean
                tem_anterior:
                  type: boolean
      400:
        description: Parâmetros inválidos
      500:
        description: Erro interno do servidor
    """
    try:
        # Parâmetros de paginação
        pagina = request.args.get('pagina', 1, type=int)
        limite = request.args.get('limite', 20, type=int)
        
        # Parâmetros de filtro
        filtros = {}
        
        if request.args.get('author'):
            filtros['author'] = request.args.get('author')
        
        if request.args.get('book_id'):
            filtros['book_id'] = request.args.get('book_id', type=int)
        
        if request.args.get('chapter'):
            filtros['chapter'] = request.args.get('chapter', type=int)
        
        if request.args.get('tags'):
            filtros['tags'] = request.args.get('tags')
        
        if request.args.get('start_date'):
            try:
                filtros['start_date'] = datetime.strptime(
                    request.args.get('start_date'), '%Y-%m-%d'
                ).date()
            except ValueError:
                return jsonify({"erro": "Formato de data inválido para start_date. Use YYYY-MM-DD"}), 400
        
        if request.args.get('end_date'):
            try:
                filtros['end_date'] = datetime.strptime(
                    request.args.get('end_date'), '%Y-%m-%d'
                ).date()
            except ValueError:
                return jsonify({"erro": "Formato de data inválido para end_date. Use YYYY-MM-DD"}), 400
        
        if request.args.get('search_text'):
            filtros['search_text'] = request.args.get('search_text')
        
        devotional_service = DevotionalService()
        resultado, status_code = devotional_service.listar_devocionais(
            filtros=filtros if filtros else None,
            pagina=pagina,
            limite=limite
        )
        
        return jsonify(resultado), status_code
        
    except Exception as e:
        print(f"Erro ao listar devocionais: {traceback.format_exc()}")
        return jsonify({"erro": "Erro interno do servidor"}), 500


@devotional_blueprint.route('/devocionais/<int:devocional_id>', methods=['PUT'])
@token_required
def atualizar_devocional(devocional_id):
    """
    Atualiza um devocional existente
    ---
    tags:
      - Devocionais
    security:
      - BearerAuth: []
    parameters:
      - in: header
        name: Authorization
        required: true
        type: string
      - in: path
        name: devocional_id
        required: true
        type: integer
        description: ID do devocional
      - in: body
        name: body
        required: true
        schema:
          type: object
          properties:
            title:
              type: string
              minLength: 3
              maxLength: 500
            main_verse:
              type: string
            verse_reference:
              type: string
            book_id:
              type: integer
              minimum: 1
              maximum: 66
            chapter:
              type: integer
              minimum: 1
            verse:
              type: integer
              minimum: 1
            content:
              type: string
              minLength: 10
            application:
              type: string
              minLength: 10
            prayer:
              type: string
              minLength: 5
            author:
              type: string
              maxLength: 200
            publish_date:
              type: string
              format: date
            tags:
              type: string
    responses:
      200:
        description: Devocional atualizado com sucesso
        schema:
          type: object
          properties:
            mensagem:
              type: string
              example: "Devocional atualizado com sucesso"
            id:
              type: integer
            campos_alterados:
              type: array
              items:
                type: string
      400:
        description: Dados inválidos
      401:
        description: Token inválido ou expirado
      404:
        description: Devocional não encontrado
      409:
        description: Conflito - título/autor duplicado
      500:
        description: Erro interno do servidor
    """
    try:
        novos_dados = request.get_json()
        
        if not novos_dados:
            return jsonify({"erro": "Dados JSON são obrigatórios"}), 400
        
        devotional_service = DevotionalService()
        resultado, status_code = devotional_service.atualizar_devocional(
            devocional_id, novos_dados
        )
        
        return jsonify(resultado), status_code
        
    except BadRequest:
        return jsonify({"erro": "JSON inválido"}), 400
    except Exception as e:
        print(f"Erro ao atualizar devocional: {traceback.format_exc()}")
        return jsonify({"erro": "Erro interno do servidor"}), 500


@devotional_blueprint.route('/devocionais/<int:devocional_id>', methods=['DELETE'])
@token_required
def deletar_devocional(devocional_id):
    """
    Deleta um devocional
    ---
    tags:
      - Devocionais
    security:
      - BearerAuth: []
    parameters:
      - in: header
        name: Authorization
        required: true
        type: string
      - in: path
        name: devocional_id
        required: true
        type: integer
        description: ID do devocional
    responses:
      200:
        description: Devocional deletado com sucesso
        schema:
          type: object
          properties:
            mensagem:
              type: string
              example: "Devocional deletado com sucesso"
      400:
        description: ID inválido
      401:
        description: Token inválido ou expirado
      404:
        description: Devocional não encontrado
      500:
        description: Erro interno do servidor
    """
    try:
        devotional_service = DevotionalService()
        resultado, status_code = devotional_service.deletar_devocional(devocional_id)
        
        return jsonify(resultado), status_code
        
    except Exception as e:
        print(f"Erro ao deletar devocional: {traceback.format_exc()}")
        return jsonify({"erro": "Erro interno do servidor"}), 500


@devotional_blueprint.route('/devocionais/buscar', methods=['GET'])
def buscar_devocionais():
    """
    Busca devocionais por texto livre
    ---
    tags:
      - Devocionais
    parameters:
      - in: query
        name: q
        required: true
        type: string
        minLength: 2
        description: Texto a ser buscado (mínimo 2 caracteres)
      - in: query
        name: limite
        type: integer
        default: 10
        maximum: 50
        description: Limite de resultados
    responses:
      200:
        description: Resultados da busca
        schema:
          type: object
          properties:
            resultados:
              type: array
              items:
                type: object
            total:
              type: integer
            termo_busca:
              type: string
      400:
        description: Parâmetros de busca inválidos
      500:
        description: Erro interno do servidor
    """
    try:
        texto = request.args.get('q', '').strip()
        limite = request.args.get('limite', 10, type=int)
        
        if not texto:
            return jsonify({"erro": "Parâmetro 'q' é obrigatório"}), 400
        
        if limite > 50:
            limite = 50
        
        devotional_service = DevotionalService()
        resultado, status_code = devotional_service.buscar_por_texto(texto, limite)
        
        return jsonify(resultado), status_code
        
    except Exception as e:
        print(f"Erro na busca de devocionais: {traceback.format_exc()}")
        return jsonify({"erro": "Erro interno do servidor"}), 500


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
    try:
        from datetime import date
        
        hoje = date.today()
        filtros = {
            'start_date': hoje,
            'end_date': hoje
        }
        
        devotional_service = DevotionalService()
        resultado, status_code = devotional_service.listar_devocionais(
            filtros=filtros, pagina=1, limite=1
        )
        
        if status_code == 200 and resultado.get('devocionais'):
            devocional = resultado['devocionais'][0]
            return jsonify({
                "devocional_do_dia": devocional,
                "data": hoje.isoformat()
            }), 200
        else:
            return jsonify({
                "mensagem": "Nenhum devocional encontrado para hoje",
                "data": hoje.isoformat()
            }), 404
        
    except Exception as e:
        print(f"Erro ao buscar devocional de hoje: {traceback.format_exc()}")
        return jsonify({"erro": "Erro interno do servidor"}), 500