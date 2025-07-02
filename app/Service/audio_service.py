from app.Repository.audio_repositorio import AudioRepository
from app.Models.audio_models import AudioInfo, DevocionalAudio, AudioEstatisticas
from typing import Optional, Dict, List, Tuple
from datetime import date
import traceback


class AudioService:
    
    def __init__(self):
        self.audio_repository = AudioRepository()

    def obter_audio_devocional(self, devotional_id: int, tipo: str) -> Tuple[Optional[bytes], str, int]:
        """
        Obtém áudio do devocional com validações de negócio
        
        Args:
            devotional_id: ID do devocional
            tipo: 'masculino' ou 'feminino'
            
        Returns:
            Tuple: (audio_bytes, content_type, status_code)
        """
        try:
            # Validações de entrada
            if not isinstance(devotional_id, int) or devotional_id <= 0:
                return None, "application/json", 400
            
            if tipo not in ['masculino', 'feminino']:
                return None, "application/json", 400
            
            # Verificar se devocional existe
            if not self.audio_repository.verificar_devocional_existe(devotional_id):
                return None, "application/json", 404
            
            # Buscar áudio
            audio_data = self.audio_repository.buscar_audio_devocional(devotional_id, tipo)
            
            if not audio_data:
                return None, "application/json", 404
            
            # Detectar tipo de content
            content_type = self._detectar_tipo_audio(audio_data)
            
            print(f"[AUDIO SERVICE] Áudio encontrado - ID: {devotional_id}, Tipo: {tipo}, Tamanho: {len(audio_data)} bytes")
            
            return audio_data, content_type, 200
            
        except Exception as e:
            print(f"[ERRO AUDIO SERVICE] {e}")
            print(f"[TRACEBACK] {traceback.format_exc()}")
            return None, "application/json", 500

    def obter_devocional_do_dia(self) -> Tuple[Dict, int]:
        """
        Obtém devocional do dia com informações de áudio
        
        Returns:
            Tuple: (response_dict, status_code)
        """
        try:
            hoje = date.today()
            print(f"[AUDIO SERVICE] Buscando devocional do dia: {hoje}")
            
            # Buscar devocional do dia
            devocional = self.audio_repository.buscar_devocional_por_data(hoje)
            
            if not devocional:
                return {"erro": "Nenhum devocional encontrado para hoje"}, 404
            
            print(f"[AUDIO SERVICE] Devocional encontrado: {devocional.title}")
            
            # Retornar dados formatados
            response = devocional.to_dict()
            
            return response, 200
            
        except Exception as e:
            print(f"[ERRO DEVOCIONAL HOJE SERVICE] {e}")
            print(f"[TRACEBACK] {traceback.format_exc()}")
            return {"erro": "Erro interno do servidor"}, 500

    def listar_devocionais_com_audio(self, limit: int = 10) -> Tuple[Dict, int]:
        """
        Lista devocionais que têm áudio disponível
        
        Args:
            limit: Limite de resultados (1-50)
            
        Returns:
            Tuple: (response_dict, status_code)
        """
        try:
            # Validar limite
            if not isinstance(limit, int) or limit < 1 or limit > 50:
                return {"erro": "Limite deve estar entre 1 e 50"}, 400
            
            print(f"[AUDIO SERVICE] Listando devocionais com áudio - Limit: {limit}")
            
            # Buscar devocionais
            devocionais = self.audio_repository.listar_devocionais_com_audio(limit)
            
            if not devocionais:
                return {"erro": "Nenhum devocional com áudio encontrado"}, 404
            
            # Montar resposta
            result = {
                "total": len(devocionais),
                "limit": limit,
                "devocionais": [dev.to_dict() for dev in devocionais]
            }
            
            print(f"[AUDIO SERVICE] {len(devocionais)} devocionais encontrados")
            
            return result, 200
            
        except Exception as e:
            print(f"[ERRO LISTAR AUDIO SERVICE] {e}")
            print(f"[TRACEBACK] {traceback.format_exc()}")
            return {"erro": "Erro interno do servidor"}, 500

    def obter_estatisticas_audio(self) -> Tuple[Dict, int]:
        """
        Obtém estatísticas dos áudios disponíveis
        
        Returns:
            Tuple: (response_dict, status_code)
        """
        try:
            print("[AUDIO SERVICE] Buscando estatísticas de áudio")
            
            estatisticas = self.audio_repository.obter_estatisticas_audio()
            
            result = estatisticas.to_dict()
            
            print(f"[AUDIO SERVICE] Estatísticas: {result['total_devocionais_com_audio']} devocionais com áudio")
            
            return result, 200
            
        except Exception as e:
            print(f"[ERRO ESTATISTICAS SERVICE] {e}")
            print(f"[TRACEBACK] {traceback.format_exc()}")
            return {"erro": "Erro interno do servidor"}, 500

    def validar_acesso_audio(self, devotional_id: int, tipo: str) -> Tuple[bool, str, int]:
        """
        Valida se é possível acessar um áudio específico
        
        Args:
            devotional_id: ID do devocional
            tipo: 'masculino' ou 'feminino'
            
        Returns:
            Tuple: (is_valid, message, status_code)
        """
        try:
            # Validações básicas
            if not isinstance(devotional_id, int) or devotional_id <= 0:
                return False, "ID do devocional inválido", 400
            
            if tipo not in ['masculino', 'feminino']:
                return False, "Tipo deve ser 'masculino' ou 'feminino'", 400
            
            # Verificar se devocional existe
            if not self.audio_repository.verificar_devocional_existe(devotional_id):
                return False, "Devocional não encontrado", 404
            
            # Verificar se áudio existe
            has_audio = self.audio_repository.verificar_audios_disponiveis(devotional_id)
            
            if not has_audio.get(tipo, False):
                return False, f"Áudio {tipo} não disponível para este devocional", 404
            
            print(f"[AUDIO SERVICE] Validação OK - ID: {devotional_id}, Tipo: {tipo}")
            
            return True, "Áudio válido", 200
            
        except Exception as e:
            print(f"[ERRO VALIDAR AUDIO SERVICE] {e}")
            return False, "Erro interno do servidor", 500

    def obter_informacoes_devocional_com_audio(self, devotional_id: int) -> Tuple[Dict, int]:
        """
        Obtém informações completas do devocional com status dos áudios
        
        Args:
            devotional_id: ID do devocional
            
        Returns:
            Tuple: (response_dict, status_code)
        """
        try:
            # Validar ID
            if not isinstance(devotional_id, int) or devotional_id <= 0:
                return {"erro": "ID do devocional inválido"}, 400
            
            print(f"[AUDIO SERVICE] Buscando info devocional - ID: {devotional_id}")
            
            # Buscar devocional
            devocional = self.audio_repository.buscar_devocional_por_id(devotional_id)
            
            if not devocional:
                return {"erro": "Devocional não encontrado"}, 404
            
            # Montar resposta completa com informações de áudio
            response = devocional.to_dict()
            
            # Adicionar informações extras de áudio
            response['audio_status'] = {
                'has_audio': response['has_audio'],
                'available_types': [tipo for tipo, disponivel in response['has_audio'].items() if disponivel],
                'audio_links': response['audio_links']
            }
            
            print(f"[AUDIO SERVICE] Info encontrada: {devocional.title}")
            
            return response, 200
            
        except Exception as e:
            print(f"[ERRO INFO DEVOCIONAL SERVICE] {e}")
            print(f"[TRACEBACK] {traceback.format_exc()}")
            return {"erro": "Erro interno do servidor"}, 500

    def obter_info_audio_especifico(self, devotional_id: int, tipo: str) -> Tuple[Dict, int]:
        """
        Obtém informações específicas sobre um áudio (sem baixar o arquivo)
        
        Args:
            devotional_id: ID do devocional
            tipo: 'masculino' ou 'feminino'
            
        Returns:
            Tuple: (response_dict, status_code)
        """
        try:
            # Validar parâmetros
            is_valid, message, status_code = self.validar_acesso_audio(devotional_id, tipo)
            
            if not is_valid:
                return {"erro": message}, status_code
            
            # Obter informações do áudio
            audio_info = self.audio_repository.obter_info_audio(devotional_id, tipo)
            
            if not audio_info:
                return {"erro": "Informações do áudio não disponíveis"}, 404
            
            response = {
                "devotional_id": audio_info.devotional_id,
                "tipo": audio_info.tipo,
                "content_type": audio_info.content_type,
                "tamanho_bytes": audio_info.tamanho,
                "tamanho_mb": round(audio_info.tamanho / (1024 * 1024), 2),
                "audio_link": f"/devotional/{devotional_id}/audio/{tipo}",
                "download_link": f"/devotional/{devotional_id}/download/{tipo}"
            }
            
            return response, 200
            
        except Exception as e:
            print(f"[ERRO INFO AUDIO SERVICE] {e}")
            return {"erro": "Erro interno do servidor"}, 500

    def _detectar_tipo_audio(self, audio_data: bytes) -> str:
        """
        Detecta o tipo de áudio baseado nos primeiros bytes
        
        Args:
            audio_data: Bytes do áudio
            
        Returns:
            Content-type do áudio
        """
        if not audio_data or len(audio_data) < 4:
            return 'audio/mpeg'  # Padrão
        
        # Primeiros bytes para diferentes formatos
        if audio_data[:3] == b'ID3' or audio_data[:2] == b'\xff\xfb':
            return 'audio/mpeg'  # MP3
        elif audio_data[:4] == b'RIFF':
            return 'audio/wav'   # WAV
        elif audio_data[:4] == b'fLaC':
            return 'audio/flac'  # FLAC
        elif audio_data[:4] == b'OggS':
            return 'audio/ogg'   # OGG
        else:
            return 'audio/mpeg'  # Padrão para MP3

    def verificar_saude_sistema_audio(self) -> Tuple[Dict, int]:
        """
        Verifica a saúde do sistema de áudio
        
        Returns:
            Tuple: (response_dict, status_code)
        """
        try:
            estatisticas = self.audio_repository.obter_estatisticas_audio()
            
            # Verificar se há pelo menos alguns áudios
            tem_audios = estatisticas.total_devocionais_com_audio > 0
            
            # Verificar balanceamento entre tipos
            balanceamento_ok = abs(estatisticas.audios_masculinos - estatisticas.audios_femininos) <= (estatisticas.total_devocionais_com_audio * 0.3)
            
            status = "saudavel" if tem_audios and balanceamento_ok else "atencao"
            
            response = {
                "status": status,
                "tem_audios": tem_audios,
                "balanceamento_ok": balanceamento_ok,
                "estatisticas": estatisticas.to_dict(),
                "recomendacoes": []
            }
            
            # Adicionar recomendações
            if not tem_audios:
                response["recomendacoes"].append("Sistema sem áudios disponíveis")
            
            if not balanceamento_ok:
                response["recomendacoes"].append("Balanceamento entre tipos de voz pode ser melhorado")
            
            if estatisticas.total_devocionais_com_audio < 10:
                response["recomendacoes"].append("Considere adicionar mais áudios para melhor experiência")
            
            return response, 200
            
        except Exception as e:
            print(f"[ERRO SAUDE SISTEMA] {e}")
            return {"erro": "Erro ao verificar saúde do sistema"}, 500