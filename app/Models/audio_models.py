from dataclasses import dataclass
from typing import Optional, Dict, Any
from datetime import date



@dataclass
class AudioInfo:
    """
    Modelo para informações de áudio
    """
    devotional_id: int
    tipo: str  # 'masculino' ou 'feminino'
    audio_data: Optional[bytes] = None
    content_type: str = 'audio/mpeg'
    tamanho: Optional[int] = None
    
    def __post_init__(self):
        if self.tipo not in ['masculino', 'feminino']:
            raise ValueError("Tipo deve ser 'masculino' ou 'feminino'")
        
        if self.audio_data and self.tamanho is None:
            self.tamanho = len(self.audio_data)


@dataclass
class DevocionalAudio:
    """
    Modelo para devocional com informações de áudio
    """
    id: int
    title: str
    main_verse: str
    verse_reference: str
    content: str
    application: str
    prayer: str
    author: str
    publish_date: Optional[date]
    tags: Optional[str]
    has_audio_masculino: bool = False
    has_audio_feminino: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte para dicionário"""
        return {
            'id': self.id,
            'title': self.title,
            'main_verse': self.main_verse,
            'verse_reference': self.verse_reference,
            'content': self.content,
            'application': self.application,
            'prayer': self.prayer,
            'author': self.author,
            'publish_date': self.publish_date.isoformat() if self.publish_date else None,
            'tags': self.tags,
            'has_audio': {
                'masculino': self.has_audio_masculino,
                'feminino': self.has_audio_feminino
            },
            'audio_links': self._get_audio_links()
        }
    
    def _get_audio_links(self) -> Dict[str, str]:
        """Gera links dos áudios disponíveis"""
        links = {}
        if self.has_audio_masculino:
            links['masculino'] = f"/devotional/{self.id}/audio/masculino"
        if self.has_audio_feminino:
            links['feminino'] = f"/devotional/{self.id}/audio/feminino"
        return links
    
    
    
    
@dataclass
class AudioEstatisticas:
    """
    Modelo para estatísticas de áudio
    """
    total_devocionais_com_audio: int
    audios_masculinos: int
    audios_femininos: int
    
    @property
    def porcentagem_masculino(self) -> float:
        """Porcentagem de devocionais com áudio masculino"""
        if self.total_devocionais_com_audio == 0:
            return 0.0
        return round((self.audios_masculinos / self.total_devocionais_com_audio) * 100, 2)
    
    @property
    def porcentagem_feminino(self) -> float:
        """Porcentagem de devocionais com áudio feminino"""
        if self.total_devocionais_com_audio == 0:
            return 0.0
        return round((self.audios_femininos / self.total_devocionais_com_audio) * 100, 2)
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte para dicionário"""
        return {
            'total_devocionais_com_audio': self.total_devocionais_com_audio,
            'audios_masculinos': self.audios_masculinos,
            'audios_femininos': self.audios_femininos,
            'porcentagem_com_audio': {
                'masculino': self.porcentagem_masculino,
                'feminino': self.porcentagem_feminino
            }
        }