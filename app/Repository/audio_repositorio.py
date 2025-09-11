from app.Config.production_database import get_db_connection
from app.Models.audio_models import AudioInfo, DevocionalAudio, AudioEstatisticas
from typing import Optional, Dict, List
from datetime import date
import traceback


class AudioRepository:
    
    @staticmethod
    def buscar_audio_devocional(devotional_id: int, tipo: str) -> Optional[bytes]:
        """
        Busca áudio do devocional no banco de dados
        
        Args:
            devotional_id: ID do devocional
            tipo: 'masculino' ou 'feminino'
            
        Returns:
            bytes do áudio ou None se não encontrado
        """
        db = None
        try:
            db = get_db_connection()
            
            # Valida tipo
            if tipo not in ['masculino', 'feminino']:
                raise ValueError("Tipo deve ser 'masculino' ou 'feminino'")
            
            campo_audio = "pt_br_masculino" if tipo == "masculino" else "pt_br_feminino"
            
            sql = f"SELECT {campo_audio} FROM devotionals_flow WHERE id = %s"
            db.cursor.execute(sql, (devotional_id,))
            
            result = db.cursor.fetchone()
            
            if result and result[0]:
                return bytes(result[0])  # Converte bytea para bytes
            
            return None
            
        except Exception as e:
            print(f"[ERRO BUSCAR AUDIO] {e}")
            print(f"[TRACEBACK] {traceback.format_exc()}")
            return None
        finally:
            if db:
                db.close()

    @staticmethod
    def buscar_devocional_por_data(data: date) -> Optional[DevocionalAudio]:
        """
        Busca devocional por data de publicação
        
        Args:
            data: Data de publicação
            
        Returns:
            DevocionalAudio ou None
        """
        db = None
        try:
            db = get_db_connection()
            
            sql = """
            SELECT id, title, main_verse, verse_reference, content, 
                   application, prayer, author, publish_date, tags,
                   CASE WHEN pt_br_masculino IS NOT NULL THEN true ELSE false END as tem_masculino,
                   CASE WHEN pt_br_feminino IS NOT NULL THEN true ELSE false END as tem_feminino
            FROM devotionals_flow 
            WHERE publish_date = %s 
            LIMIT 1
            """
            
            db.cursor.execute(sql, (data,))
            result = db.cursor.fetchone()
            
            if result:
                return DevocionalAudio(
                    id=result[0],
                    title=result[1],
                    main_verse=result[2],
                    verse_reference=result[3],
                    content=result[4],
                    application=result[5],
                    prayer=result[6],
                    author=result[7],
                    publish_date=result[8],
                    tags=result[9],
                    has_audio_masculino=result[10],
                    has_audio_feminino=result[11]
                )
            
            return None
            
        except Exception as e:
            print(f"[ERRO BUSCAR DEVOCIONAL DATA] {e}")
            print(f"[TRACEBACK] {traceback.format_exc()}")
            return None
        finally:
            if db:
                db.close()

    @staticmethod
    def verificar_audios_disponiveis(devotional_id: int) -> Dict[str, bool]:
        """
        Verifica quais áudios estão disponíveis para um devocional
        
        Args:
            devotional_id: ID do devocional
            
        Returns:
            Dict com disponibilidade: {'masculino': bool, 'feminino': bool}
        """
        db = None
        try:
            db = get_db_connection()
            
            sql = """
            SELECT 
                CASE WHEN pt_br_masculino IS NOT NULL THEN true ELSE false END as tem_masculino,
                CASE WHEN pt_br_feminino IS NOT NULL THEN true ELSE false END as tem_feminino
            FROM devotionals_flow 
            WHERE id = %s
            """
            
            db.cursor.execute(sql, (devotional_id,))
            result = db.cursor.fetchone()
            
            if result:
                return {
                    "masculino": result[0],
                    "feminino": result[1]
                }
            
            return {"masculino": False, "feminino": False}
            
        except Exception as e:
            print(f"[ERRO VERIFICAR AUDIOS] {e}")
            print(f"[TRACEBACK] {traceback.format_exc()}")
            return {"masculino": False, "feminino": False}
        finally:
            if db:
                db.close()

    @staticmethod
    def listar_devocionais_com_audio(limit: int = 10) -> List[DevocionalAudio]:
        """
        Lista devocionais que têm pelo menos um áudio
        
        Args:
            limit: Limite de resultados
            
        Returns:
            Lista de DevocionalAudio
        """
        db = None
        try:
            db = get_db_connection()
            
            sql = """
            SELECT id, title, main_verse, verse_reference, content, application, prayer, 
                   author, publish_date, tags,
                   CASE WHEN pt_br_masculino IS NOT NULL THEN true ELSE false END as tem_masculino,
                   CASE WHEN pt_br_feminino IS NOT NULL THEN true ELSE false END as tem_feminino
            FROM devotionals_flow 
            WHERE pt_br_masculino IS NOT NULL OR pt_br_feminino IS NOT NULL
            ORDER BY publish_date DESC
            LIMIT %s
            """
            
            db.cursor.execute(sql, (limit,))
            results = db.cursor.fetchall()
            
            devocionais = []
            for row in results:
                devocionais.append(DevocionalAudio(
                    id=row[0],
                    title=row[1],
                    main_verse=row[2],
                    verse_reference=row[3],
                    content=row[4],
                    application=row[5],
                    prayer=row[6],
                    author=row[7],
                    publish_date=row[8],
                    tags=row[9],
                    has_audio_masculino=row[10],
                    has_audio_feminino=row[11]
                ))
            
            return devocionais
            
        except Exception as e:
            print(f"[ERRO LISTAR DEVOCIONAIS AUDIO] {e}")
            print(f"[TRACEBACK] {traceback.format_exc()}")
            return []
        finally:
            if db:
                db.close()

    @staticmethod
    def buscar_devocional_por_id(devotional_id: int) -> Optional[DevocionalAudio]:
        """
        Busca devocional completo por ID
        
        Args:
            devotional_id: ID do devocional
            
        Returns:
            DevocionalAudio ou None
        """
        db = None
        try:
            db = get_db_connection()
            
            sql = """
            SELECT id, title, main_verse, verse_reference, content, application, prayer,
                   author, publish_date, tags,
                   CASE WHEN pt_br_masculino IS NOT NULL THEN true ELSE false END as tem_masculino,
                   CASE WHEN pt_br_feminino IS NOT NULL THEN true ELSE false END as tem_feminino
            FROM devotionals_flow 
            WHERE id = %s
            """
            
            db.cursor.execute(sql, (devotional_id,))
            result = db.cursor.fetchone()
            
            if result:
                return DevocionalAudio(
                    id=result[0],
                    title=result[1],
                    main_verse=result[2],
                    verse_reference=result[3],
                    content=result[4],
                    application=result[5],
                    prayer=result[6],
                    author=result[7],
                    publish_date=result[8],
                    tags=result[9],
                    has_audio_masculino=result[10],
                    has_audio_feminino=result[11]
                )
            
            return None
            
        except Exception as e:
            print(f"[ERRO BUSCAR DEVOCIONAL ID] {e}")
            print(f"[TRACEBACK] {traceback.format_exc()}")
            return None
        finally:
            if db:
                db.close()

    @staticmethod
    def obter_estatisticas_audio() -> AudioEstatisticas:
        """
        Obtém estatísticas dos áudios disponíveis
        
        Returns:
            AudioEstatisticas
        """
        db = None
        try:
            db = get_db_connection()
            
            sql = """
            SELECT 
                COUNT(CASE WHEN pt_br_masculino IS NOT NULL THEN 1 END) as masculino,
                COUNT(CASE WHEN pt_br_feminino IS NOT NULL THEN 1 END) as feminino,
                COUNT(CASE WHEN pt_br_masculino IS NOT NULL OR pt_br_feminino IS NOT NULL THEN 1 END) as total
            FROM devotionals_flow
            """
            
            db.cursor.execute(sql)
            result = db.cursor.fetchone()
            
            if result:
                return AudioEstatisticas(
                    audios_masculinos=result[0],
                    audios_femininos=result[1],
                    total_devocionais_com_audio=result[2]
                )
            
            return AudioEstatisticas(
                audios_masculinos=0,
                audios_femininos=0,
                total_devocionais_com_audio=0
            )
            
        except Exception as e:
            print(f"[ERRO ESTATISTICAS AUDIO] {e}")
            print(f"[TRACEBACK] {traceback.format_exc()}")
            return AudioEstatisticas(
                audios_masculinos=0,
                audios_femininos=0,
                total_devocionais_com_audio=0
            )
        finally:
            if db:
                db.close()

    @staticmethod
    def verificar_devocional_existe(devotional_id: int) -> bool:
        """
        Verifica se um devocional existe
        
        Args:
            devotional_id: ID do devocional
            
        Returns:
            True se existe, False caso contrário
        """
        db = None
        try:
            db = get_db_connection()
            
            sql = "SELECT 1 FROM devotionals_flow WHERE id = %s LIMIT 1"
            db.cursor.execute(sql, (devotional_id,))
            
            return db.cursor.fetchone() is not None
            
        except Exception as e:
            print(f"[ERRO VERIFICAR DEVOCIONAL] {e}")
            return False
        finally:
            if db:
                db.close()

    @staticmethod
    def obter_info_audio(devotional_id: int, tipo: str) -> Optional[AudioInfo]:
        """
        Obtém informações detalhadas sobre um áudio específico
        
        Args:
            devotional_id: ID do devocional
            tipo: 'masculino' ou 'feminino'
            
        Returns:
            AudioInfo ou None
        """
        try:
            audio_data = AudioRepository.buscar_audio_devocional(devotional_id, tipo)
            
            if audio_data:
                return AudioInfo(
                    devotional_id=devotional_id,
                    tipo=tipo,
                    audio_data=audio_data,
                    tamanho=len(audio_data)
                )
            
            return None
            
        except Exception as e:
            print(f"[ERRO INFO AUDIO] {e}")
            return None