from flask import Blueprint, jsonify, request, Response, send_file
from app.Service.audio_service import AudioService
from werkzeug.exceptions import BadRequest
import tempfile
import os
import traceback


audio_blueprint = Blueprint('audio', __name__)


@audio_blueprint.route('/devotional/<int:devotional_id>/audio/<tipo>', methods=['GET'])
def servir_audio_devocional(devotional_id, tipo):
    """
    Serve o áudio do devocional diretamente no navegador
    ---
    tags:
      - Áudios
    parameters:
      - in: path
        name: devotional_id
        type: integer
        required: true
        description: ID do devocional
        example: 1
      - in: path
        name: tipo
        type: string
        required: true
        enum: ['masculino', 'feminino']
        description: Tipo de voz (masculino ou feminino)
        example: "masculino"
    responses:
      200:
        description: Áudio do devocional
        content:
          audio/mpeg:
            schema:
              type: string
              format: binary
      400:
        description: Parâmetros inválidos
        schema:
          type: object
          properties:
            erro:
              type: string
              example: "Tipo deve ser 'masculino' ou 'feminino'"
      404:
        description: Devocional ou áudio não encontrado
        schema:
          type: object
          properties:
            erro:
              type: string
              example: "Áudio não encontrado"
      500:
        description: Erro interno do servidor
    """
    try:
        print(f"[DEBUG AUDIO] Buscando áudio - ID: {devotional_id}, Tipo: {tipo}")
        
        audio_service = AudioService()
        
        # Obter áudio através do service
        audio_data, content_type, status_code = audio_service.obter_audio_devocional(devotional_id, tipo)
        
        if status_code != 200:
            if status_code == 400:
                return jsonify({"erro": "Parâmetros inválidos"}), 400
            elif status_code == 404:
                return jsonify({"erro": "Áudio não encontrado"}), 404
            else:
                return jsonify({"erro": "Erro interno"}), 500
        
        print(f"[DEBUG AUDIO] Áudio encontrado - Tamanho: {len(audio_data)} bytes, Content-Type: {content_type}")
        
        # Retornar áudio com headers corretos
        return Response(
            audio_data,
            mimetype=content_type,
            headers={
                "Content-Disposition": f"inline; filename=devocional_{devotional_id}_{tipo}.mp3",
                "Accept-Ranges": "bytes",
                "Content-Length": str(len(audio_data)),
                "Cache-Control": "public, max-age=3600"  # Cache por 1 hora
            }
        )
        
    except Exception as e:
        print(f"[ERRO AUDIO ROUTE] {e}")
        print(f"[TRACEBACK] {traceback.format_exc()}")
        return jsonify({"erro": "Erro interno do servidor"}), 500


@audio_blueprint.route('/devotional/hoje', methods=['GET'])
def devocional_do_dia():
    """
    Retorna o devocional do dia com links para áudios
    ---
    tags:
      - Devocionais
    responses:
      200:
        description: Devocional do dia com informações de áudio
        schema:
          type: object
          properties:
            id:
              type: integer
              example: 1
            title:
              type: string
              example: "A Paz que Excede Todo Entendimento"
            main_verse:
              type: string
              example: "E a paz de Deus, que excede todo o entendimento..."
            verse_reference:
              type: string
              example: "Filipenses 4:7"
            content:
              type: string
              example: "Em meio às turbulências da vida..."
            application:
              type: string
              example: "Hoje, quando você se sentir ansioso..."
            prayer:
              type: string
              example: "Senhor, obrigado pela paz que só Tu podes dar..."
            author:
              type: string
              example: "Pastor João Silva"
            publish_date:
              type: string
              format: date
              example: "2025-06-29"
            tags:
              type: string
              example: "paz, ansiedade, confiança, fé"
            has_audio:
              type: object
              properties:
                masculino:
                  type: boolean
                  example: true
                feminino:
                  type: boolean
                  example: false
            audio_links:
              type: object
              properties:
                masculino:
                  type: string
                  example: "/devotional/1/audio/masculino"
                feminino:
                  type: string
                  example: "/devotional/1/audio/feminino"
      404:
        description: Nenhum devocional encontrado para hoje
        schema:
          type: object
          properties:
            erro:
              type: string
              example: "Nenhum devocional encontrado para hoje"
      500:
        description: Erro interno do servidor
    """
    try:
        print("[DEBUG HOJE] Buscando devocional do dia")
        
        audio_service = AudioService()
        resultado, status_code = audio_service.obter_devocional_do_dia()
        
        print(f"[DEBUG HOJE] Resultado: Status {status_code}")
        
        return jsonify(resultado), status_code
        
    except Exception as e:
        print(f"[ERRO HOJE ROUTE] {e}")
        print(f"[TRACEBACK] {traceback.format_exc()}")
        return jsonify({"erro": "Erro interno do servidor"}), 500


# @audio_blueprint.route('/devotionals/com-audio', methods=['GET'])
# def listar_devocionais_com_audio():
#     """
#     Lista devocionais que têm áudio disponível
#     ---
#     tags:
#       - Devocionais
#     parameters:
#       - in: query
#         name: limit
#         type: integer
#         default: 10
#         minimum: 1
#         maximum: 50
#         description: Limite de resultados (1-50)
#         example: 10
#     responses:
#       200:
#         description: Lista de devocionais com áudio
#         schema:
#           type: object
#           properties:
#             total:
#               type: integer
#               example: 5
#             limit:
#               type: integer
#               example: 10
#             devocionais:
#               type: array
#               items:
#                 type: object
#                 properties:
#                   id:
#                     type: integer
#                     example: 1
#                   title:
#                     type: string
#                     example: "A Paz que Excede Todo Entendimento"
#                   author:
#                     type: string
#                     example: "Pastor João Silva"
#                   publish_date:
#                     type: string
#                     format: date
#                     example: "2025-06-29"
#                   has_audio:
#                     type: object
#                     properties:
#                       masculino:
#                         type: boolean
#                         example: true
#                       feminino:
#                         type: boolean
#                         example: false
#                   audio_links:
#                     type: object
#                     properties:
#                       masculino:
#                         type: string
#                         example: "/devotional/1/audio/masculino"
#       400:
#         description: Limite inválido
#         schema:
#           type: object
#           properties:
#             erro:
#               type: string
#               example: "Limite deve estar entre 1 e 50"
#       404:
#         description: Nenhum devocional com áudio encontrado
#       500:
#         description: Erro interno do servidor
#     """
#     try:
#         # Obter parâmetro limit
#         limit = request.args.get('limit', 10, type=int)
        
#         print(f"[DEBUG LISTA] Listando devocionais com áudio - Limit: {limit}")
        
#         audio_service = AudioService()
#         resultado, status_code = audio_service.listar_devocionais_com_audio(limit)
        
#         print(f"[DEBUG LISTA] Resultado: Status {status_code}, Total encontrado: {resultado.get('total', 0) if status_code == 200 else 'N/A'}")
        
#         return jsonify(resultado), status_code
        
#     except Exception as e:
#         print(f"[ERRO LISTA ROUTE] {e}")
#         print(f"[TRACEBACK] {traceback.format_exc()}")
#         return jsonify({"erro": "Erro interno do servidor"}), 500


@audio_blueprint.route('/devotional/<int:devotional_id>/download/<tipo>', methods=['GET'])
def download_audio_devocional(devotional_id, tipo):
    """
    Faz download do áudio do devocional
    ---
    tags:
      - Áudios
    parameters:
      - in: path
        name: devotional_id
        type: integer
        required: true
        description: ID do devocional
        example: 1
      - in: path
        name: tipo
        type: string
        required: true
        enum: ['masculino', 'feminino']
        description: Tipo de voz (masculino ou feminino)
        example: "masculino"
    responses:
      200:
        description: Download do arquivo de áudio
        content:
          audio/mpeg:
            schema:
              type: string
              format: binary
      400:
        description: Parâmetros inválidos
      404:
        description: Áudio não encontrado
      500:
        description: Erro interno do servidor
    """
    try:
        print(f"[DEBUG DOWNLOAD] Download áudio - ID: {devotional_id}, Tipo: {tipo}")
        
        audio_service = AudioService()
        
        # Obter áudio através do service
        audio_data, content_type, status_code = audio_service.obter_audio_devocional(devotional_id, tipo)
        
        if status_code != 200:
            if status_code == 400:
                return jsonify({"erro": "Parâmetros inválidos"}), 400
            elif status_code == 404:
                return jsonify({"erro": "Áudio não encontrado"}), 404
            else:
                return jsonify({"erro": "Erro interno"}), 500
        
        # Criar arquivo temporário para download
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as temp_file:
            temp_file.write(audio_data)
            temp_file.flush()
            
            filename = f"devocional_{devotional_id}_{tipo}.mp3"
            
            print(f"[DEBUG DOWNLOAD] Enviando arquivo: {filename}, Tamanho: {len(audio_data)} bytes")
            
            # Limpar arquivo temporário após envio
            def cleanup_file():
                try:
                    os.unlink(temp_file.name)
                except:
                    pass
            
            response = send_file(
                temp_file.name,
                as_attachment=True,
                download_name=filename,
                mimetype=content_type
            )
            
            # Agendar limpeza do arquivo
            response.call_on_close(cleanup_file)
            
            return response
        
    except Exception as e:
        print(f"[ERRO DOWNLOAD ROUTE] {e}")
        print(f"[TRACEBACK] {traceback.format_exc()}")
        return jsonify({"erro": "Erro interno do servidor"}), 500


@audio_blueprint.route('/devotional/<int:devotional_id>/info', methods=['GET'])
def obter_info_devocional_com_audio(devotional_id):
    """
    Obtém informações completas do devocional com status dos áudios
    ---
    tags:
      - Devocionais
    parameters:
      - in: path
        name: devotional_id
        type: integer
        required: true
        description: ID do devocional
        example: 1
    responses:
      200:
        description: Informações completas do devocional
        schema:
          type: object
          properties:
            id:
              type: integer
            title:
              type: string
            content:
              type: string
            audio_status:
              type: object
              properties:
                has_audio:
                  type: object
                available_types:
                  type: array
                  items:
                    type: string
                audio_links:
                  type: object
      400:
        description: ID inválido
      404:
        description: Devocional não encontrado
      500:
        description: Erro interno do servidor
    """
    try:
        print(f"[DEBUG INFO] Buscando info devocional - ID: {devotional_id}")
        
        audio_service = AudioService()
        resultado, status_code = audio_service.obter_informacoes_devocional_com_audio(devotional_id)
        
        print(f"[DEBUG INFO] Resultado: Status {status_code}")
        
        return jsonify(resultado), status_code
        
    except Exception as e:
        print(f"[ERRO INFO ROUTE] {e}")
        print(f"[TRACEBACK] {traceback.format_exc()}")
        return jsonify({"erro": "Erro interno do servidor"}), 500


# @audio_blueprint.route('/audio/estatisticas', methods=['GET'])
# def obter_estatisticas_audio():
#     """
#     Obtém estatísticas dos áudios disponíveis
#     ---
#     tags:
#       - Áudios
#     responses:
#       200:
#         description: Estatísticas dos áudios
#         schema:
#           type: object
#           properties:
#             total_devocionais_com_audio:
#               type: integer
#               example: 25
#             audios_masculinos:
#               type: integer
#               example: 20
#             audios_femininos:
#               type: integer
#               example: 15
#             porcentagem_com_audio:
#               type: object
#               properties:
#                 masculino:
#                   type: number
#                   example: 80.0
#                 feminino:
#                   type: number
#                   example: 60.0
#       500:
#         description: Erro interno do servidor
#     """
#     try:
#         print("[DEBUG STATS] Buscando estatísticas de áudio")
        
#         audio_service = AudioService()
#         resultado, status_code = audio_service.obter_estatisticas_audio()
        
#         print(f"[DEBUG STATS] Resultado: Status {status_code}")
        
#         return jsonify(resultado), status_code
        
#     except Exception as e:
#         print(f"[ERRO STATS ROUTE] {e}")
#         print(f"[TRACEBACK] {traceback.format_exc()}")
#         return jsonify({"erro": "Erro interno do servidor"}), 500


@audio_blueprint.route('/devotional/<int:devotional_id>/audio/<tipo>/validar', methods=['GET'])
def validar_acesso_audio(devotional_id, tipo):
    """
    Valida se é possível acessar um áudio específico
    ---
    tags:
      - Áudios
    parameters:
      - in: path
        name: devotional_id
        type: integer
        required: true
        description: ID do devocional
      - in: path
        name: tipo
        type: string
        required: true
        enum: ['masculino', 'feminino']
        description: Tipo de voz
    responses:
      200:
        description: Áudio válido e acessível
        schema:
          type: object
          properties:
            valido:
              type: boolean
              example: true
            mensagem:
              type: string
              example: "Áudio válido"
            audio_link:
              type: string
              example: "/devotional/1/audio/masculino"
      400:
        description: Parâmetros inválidos
      404:
        description: Áudio não encontrado
      500:
        description: Erro interno do servidor
    """
    try:
        print(f"[DEBUG VALIDAR] Validando áudio - ID: {devotional_id}, Tipo: {tipo}")
        
        audio_service = AudioService()
        is_valid, message, status_code = audio_service.validar_acesso_audio(devotional_id, tipo)
        
        if is_valid:
            return jsonify({
                "valido": True,
                "mensagem": message,
                "audio_link": f"/devotional/{devotional_id}/audio/{tipo}"
            }), 200
        else:
            return jsonify({
                "valido": False,
                "mensagem": message
            }), status_code
        
    except Exception as e:
        print(f"[ERRO VALIDAR ROUTE] {e}")
        print(f"[TRACEBACK] {traceback.format_exc()}")
        return jsonify({"erro": "Erro interno do servidor"}), 500


@audio_blueprint.route('/devotional/<int:devotional_id>/audio/<tipo>/info', methods=['GET'])
def obter_info_audio_especifico(devotional_id, tipo):
    """
    Obtém informações específicas sobre um áudio (tamanho, tipo, etc.)
    ---
    tags:
      - Áudios
    parameters:
      - in: path
        name: devotional_id
        type: integer
        required: true
        description: ID do devocional
      - in: path
        name: tipo
        type: string
        required: true
        enum: ['masculino', 'feminino']
        description: Tipo de voz
    responses:
      200:
        description: Informações do áudio
        schema:
          type: object
          properties:
            devotional_id:
              type: integer
            tipo:
              type: string
            content_type:
              type: string
            tamanho_bytes:
              type: integer
            tamanho_mb:
              type: number
            audio_link:
              type: string
            download_link:
              type: string
      400:
        description: Parâmetros inválidos
      404:
        description: Áudio não encontrado
      500:
        description: Erro interno do servidor
    """
    try:
        print(f"[DEBUG INFO AUDIO] Info áudio específico - ID: {devotional_id}, Tipo: {tipo}")
        
        audio_service = AudioService()
        resultado, status_code = audio_service.obter_info_audio_especifico(devotional_id, tipo)
        
        return jsonify(resultado), status_code
        
    except Exception as e:
        print(f"[ERRO INFO AUDIO ROUTE] {e}")
        print(f"[TRACEBACK] {traceback.format_exc()}")
        return jsonify({"erro": "Erro interno do servidor"}), 500


@audio_blueprint.route('/audio/saude', methods=['GET'])
def verificar_saude_sistema():
    """
    Verifica a saúde do sistema de áudio
    ---
    tags:
      - Áudios
    responses:
      200:
        description: Status da saúde do sistema
        schema:
          type: object
          properties:
            status:
              type: string
              enum: ['saudavel', 'atencao']
            tem_audios:
              type: boolean
            balanceamento_ok:
              type: boolean
            estatisticas:
              type: object
            recomendacoes:
              type: array
              items:
                type: string
      500:
        description: Erro interno do servidor
    """
    try:
        print("[DEBUG SAUDE] Verificando saúde do sistema de áudio")
        
        audio_service = AudioService()
        resultado, status_code = audio_service.verificar_saude_sistema_audio()
        
        return jsonify(resultado), status_code
        
    except Exception as e:
        print(f"[ERRO SAUDE ROUTE] {e}")
        print(f"[TRACEBACK] {traceback.format_exc()}")
        return jsonify({"erro": "Erro interno do servidor"}), 500