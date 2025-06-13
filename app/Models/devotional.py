from dataclasses import dataclass, field
from datetime import date
from typing import Optional, Dict, Any, List
import re


@dataclass
class DevotionalBase:
    """
    Classe base para devocionais com validações comuns.
    Implementa o princípio DRY evitando duplicação de validações.
    """
    title: str
    main_verse: str
    verse_reference: str
    book_id: int
    chapter: int
    verse: int
    content: str
    application: str
    prayer: str
    author: str
    publish_date: date
    tags: str

    def __post_init__(self):
        """Executa validações após inicialização"""
        self._validar_campos_obrigatorios()
        self._validar_tipos()
        self._validar_regras_negocio()
        self._normalizar_dados()

    def _validar_campos_obrigatorios(self) -> None:
        """
        Valida se todos os campos obrigatórios estão preenchidos.
        Implementa Single Responsibility Principle (SRP).
        """
        campos_obrigatorios = {
            'title': self.title,
            'main_verse': self.main_verse,
            'verse_reference': self.verse_reference,
            'content': self.content,
            'application': self.application,
            'prayer': self.prayer,
            'author': self.author,
            'publish_date': self.publish_date,
            'tags': self.tags
        }

        for campo, valor in campos_obrigatorios.items():
            if not valor or (isinstance(valor, str) and not valor.strip()):
                raise ValueError(f"Campo obrigatório '{campo}' não pode estar vazio")

    def _validar_tipos(self) -> None:
        """
        Valida tipos de dados dos campos.
        Garante integridade dos dados de entrada.
        """
        if not isinstance(self.book_id, int) or self.book_id <= 0:
            raise ValueError("book_id deve ser um número inteiro positivo")
        
        if not isinstance(self.chapter, int) or self.chapter <= 0:
            raise ValueError("chapter deve ser um número inteiro positivo")
        
        if not isinstance(self.verse, int) or self.verse <= 0:
            raise ValueError("verse deve ser um número inteiro positivo")
        
        if not isinstance(self.publish_date, date):
            raise ValueError("publish_date deve ser um objeto date válido")

    def _validar_regras_negocio(self) -> None:
        """
        Valida regras específicas de negócio.
        Implementa validações contextuais do domínio.
        """
        # Validação do título
        if len(self.title.strip()) < 5:
            raise ValueError("Título deve ter pelo menos 5 caracteres")
        
        if len(self.title.strip()) > 200:
            raise ValueError("Título não pode ter mais de 200 caracteres")

        # Validação da referência bíblica
        if not self._validar_formato_referencia_biblica(self.verse_reference):
            raise ValueError("Formato de referência bíblica inválido")

        # Validação do conteúdo
        if len(self.content.strip()) < 50:
            raise ValueError("Conteúdo deve ter pelo menos 50 caracteres")

        # Validação da aplicação
        if len(self.application.strip()) < 20:
            raise ValueError("Aplicação deve ter pelo menos 20 caracteres")

        # Validação da oração
        if len(self.prayer.strip()) < 10:
            raise ValueError("Oração deve ter pelo menos 10 caracteres")

        # Validação do autor
        if len(self.author.strip()) < 2:
            raise ValueError("Nome do autor deve ter pelo menos 2 caracteres")

        # Validação de data futura (não pode ser muito distante)
        from datetime import datetime, timedelta
        data_limite = date.today() + timedelta(days=365)  # 1 ano no futuro
        if self.publish_date > data_limite:
            raise ValueError("Data de publicação não pode ser superior a 1 ano no futuro")

    def _validar_formato_referencia_biblica(self, referencia: str) -> bool:
        """
        Valida se a referência bíblica está em formato válido.
        Exemplos válidos: "João 3:16", "1 Coríntios 13:4-7", "Salmos 23:1"
        """
        # Padrão regex para referências bíblicas comuns
        padrao = r'^[\w\s]+\s+\d+:\d+(-\d+)?$'
        return bool(re.match(padrao, referencia.strip()))

    def _normalizar_dados(self) -> None:
        """
        Normaliza dados para consistência.
        Remove espaços extras e formata adequadamente.
        """
        self.title = self.title.strip()
        self.main_verse = self.main_verse.strip()
        self.verse_reference = self.verse_reference.strip()
        self.content = self.content.strip()
        self.application = self.application.strip()
        self.prayer = self.prayer.strip()
        self.author = self.author.strip()
        self.tags = self.tags.strip()

    def to_dict(self) -> Dict[str, Any]:
        """
        Converte o objeto para dicionário.
        Útil para serialização e persistência.
        """
        return {
            'title': self.title,
            'main_verse': self.main_verse,
            'verse_reference': self.verse_reference,
            'book_id': self.book_id,
            'chapter': self.chapter,
            'verse': self.verse,
            'content': self.content,
            'application': self.application,
            'prayer': self.prayer,
            'author': self.author,
            'publish_date': self.publish_date,
            'tags': self.tags
        }


@dataclass
class DevotionalCreate(DevotionalBase):
    """
    Modelo para criação de novos devocionais.
    Herda validações da classe base e adiciona comportamentos específicos de criação.
    Implementa Open/Closed Principle (OCP) - extensível sem modificar a base.
    """
    
    def __post_init__(self):
        """Executa validações específicas de criação"""
        super().__post_init__()
        self._validar_criacao()

    def _validar_criacao(self) -> None:
        """
        Validações específicas para criação de devocionais.
        Implementa regras que só se aplicam na criação.
        """
        # Validação de data de publicação na criação
        if self.publish_date < date.today():
            # Permite datas passadas apenas se for no máximo 30 dias atrás
            from datetime import timedelta
            data_minima = date.today() - timedelta(days=30)
            if self.publish_date < data_minima:
                raise ValueError("Data de publicação não pode ser anterior a 30 dias")

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DevotionalCreate':
        """
        Cria uma instância a partir de dicionário.
        Factory method que facilita criação a partir de dados externos.
        """
        try:
            # Converte string para date se necessário
            if isinstance(data.get('publish_date'), str):
                from datetime import datetime
                data['publish_date'] = datetime.strptime(data['publish_date'], '%Y-%m-%d').date()
            
            return cls(**data)
        except TypeError as e:
            raise ValueError(f"Dados inválidos para criação do devocional: {e}")


@dataclass
class Devotional(DevotionalBase):
    """
    Modelo completo do devocional incluindo ID.
    Representa a entidade completa após persistência.
    Implementa Single Responsibility Principle (SRP).
    """
    id: int = field(init=False)  # ID é definido após persistência
    
    def __init__(self, id: int, **kwargs):
        """
        Inicializa devocional completo com ID.
        
        Args:
            id: ID único do devocional
            **kwargs: Outros campos do devocional
        """
        # Valida ID
        if not isinstance(id, int) or id <= 0:
            raise ValueError("ID deve ser um número inteiro positivo")
        
        self.id = id
        
        # Inicializa campos da classe base
        for field_name, field_obj in self.__dataclass_fields__.items():
            if field_name != 'id' and field_name in kwargs:
                setattr(self, field_name, kwargs[field_name])
        
        # Executa validações da classe base
        super().__post_init__()

    def to_dict(self) -> Dict[str, Any]:
        """
        Converte para dicionário incluindo ID.
        Override do método da classe base.
        """
        data = super().to_dict()
        data['id'] = self.id
        return data

    def atualizar(self, **kwargs) -> 'Devotional':
        """
        Retorna nova instância com campos atualizados.
        Implementa imutabilidade e evita efeitos colaterais.
        """
        dados_atuais = self.to_dict()
        dados_atuais.update(kwargs)
        
        return Devotional(**dados_atuais)


@dataclass
class DevotionalUpdate:
    """
    Modelo para atualização de devocionais.
    Todos os campos são opcionais para permitir atualizações parciais.
    Implementa Interface Segregation Principle (ISP).
    """
    title: Optional[str] = None
    main_verse: Optional[str] = None
    verse_reference: Optional[str] = None
    book_id: Optional[int] = None
    chapter: Optional[int] = None
    verse: Optional[int] = None
    content: Optional[str] = None
    application: Optional[str] = None
    prayer: Optional[str] = None
    author: Optional[str] = None
    publish_date: Optional[date] = None
    tags: Optional[str] = None

    def __post_init__(self):
        """Executa validações dos campos fornecidos"""
        self._validar_campos_fornecidos()
        self._normalizar_campos_fornecidos()

    def _validar_campos_fornecidos(self) -> None:
        """
        Valida apenas os campos que foram fornecidos para atualização.
        Implementa validação condicional.
        """
        if self.title is not None:
            if not self.title.strip() or len(self.title.strip()) < 5:
                raise ValueError("Título deve ter pelo menos 5 caracteres")
            if len(self.title.strip()) > 200:
                raise ValueError("Título não pode ter mais de 200 caracteres")

        if self.book_id is not None and (not isinstance(self.book_id, int) or self.book_id <= 0):
            raise ValueError("book_id deve ser um número inteiro positivo")

        if self.chapter is not None and (not isinstance(self.chapter, int) or self.chapter <= 0):
            raise ValueError("chapter deve ser um número inteiro positivo")

        if self.verse is not None and (not isinstance(self.verse, int) or self.verse <= 0):
            raise ValueError("verse deve ser um número inteiro positivo")

        if self.content is not None and len(self.content.strip()) < 50:
            raise ValueError("Conteúdo deve ter pelo menos 50 caracteres")

        if self.application is not None and len(self.application.strip()) < 20:
            raise ValueError("Aplicação deve ter pelo menos 20 caracteres")

        if self.prayer is not None and len(self.prayer.strip()) < 10:
            raise ValueError("Oração deve ter pelo menos 10 caracteres")

        if self.author is not None and len(self.author.strip()) < 2:
            raise ValueError("Nome do autor deve ter pelo menos 2 caracteres")

    def _normalizar_campos_fornecidos(self) -> None:
        """
        Normaliza apenas os campos que foram fornecidos.
        Remove espaços extras dos campos de texto.
        """
        if self.title is not None:
            self.title = self.title.strip()
        if self.main_verse is not None:
            self.main_verse = self.main_verse.strip()
        if self.verse_reference is not None:
            self.verse_reference = self.verse_reference.strip()
        if self.content is not None:
            self.content = self.content.strip()
        if self.application is not None:
            self.application = self.application.strip()
        if self.prayer is not None:
            self.prayer = self.prayer.strip()
        if self.author is not None:
            self.author = self.author.strip()
        if self.tags is not None:
            self.tags = self.tags.strip()

    def to_dict(self) -> Dict[str, Any]:
        """
        Converte para dicionário apenas com campos que não são None.
        Útil para atualizações parciais no banco de dados.
        """
        return {
            campo: valor
            for campo, valor in {
                'title': self.title,
                'main_verse': self.main_verse,
                'verse_reference': self.verse_reference,
                'book_id': self.book_id,
                'chapter': self.chapter,
                'verse': self.verse,
                'content': self.content,
                'application': self.application,
                'prayer': self.prayer,
                'author': self.author,
                'publish_date': self.publish_date,
                'tags': self.tags
            }.items()
            if valor is not None
        }

    def tem_campos_para_atualizar(self) -> bool:
        """
        Verifica se há pelo menos um campo para atualizar.
        Evita operações desnecessárias no banco.
        """
        return any(valor is not None for valor in [
            self.title, self.main_verse, self.verse_reference, self.book_id,
            self.chapter, self.verse, self.content, self.application,
            self.prayer, self.author, self.publish_date, self.tags
        ])

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DevotionalUpdate':
        """
        Cria instância a partir de dicionário.
        Ignora campos não reconhecidos e converte tipos quando necessário.
        """
        campos_validos = {
            'title', 'main_verse', 'verse_reference', 'book_id',
            'chapter', 'verse', 'content', 'application',
            'prayer', 'author', 'publish_date', 'tags'
        }
        
        # Filtra apenas campos válidos
        dados_filtrados = {k: v for k, v in data.items() if k in campos_validos}
        
        # Converte string para date se necessário
        if 'publish_date' in dados_filtrados and isinstance(dados_filtrados['publish_date'], str):
            from datetime import datetime
            dados_filtrados['publish_date'] = datetime.strptime(dados_filtrados['publish_date'], '%Y-%m-%d').date()
        
        return cls(**dados_filtrados)


@dataclass
class DevotionalFilter:
    """
    Modelo para filtros de busca de devocionais.
    Implementa Dependency Inversion Principle (DIP) - abstração para filtros.
    """
    author: Optional[str] = None
    tags: Optional[str] = None
    book_id: Optional[int] = None
    data_inicio: Optional[date] = None
    data_fim: Optional[date] = None
    page: int = 1
    per_page: int = 10

    def __post_init__(self):
        """Valida parâmetros de filtro"""
        if self.page < 1:
            raise ValueError("Página deve ser maior que 0")
        
        if self.per_page < 1 or self.per_page > 100:
            raise ValueError("Items por página deve estar entre 1 e 100")
        
        if self.book_id is not None and self.book_id <= 0:
            raise ValueError("book_id deve ser um número positivo")
        
        if self.data_inicio and self.data_fim and self.data_inicio > self.data_fim:
            raise ValueError("Data de início não pode ser posterior à data fim")

    def to_dict(self) -> Dict[str, Any]:
        """Converte filtros para dicionário, ignorando valores None"""
        return {k: v for k, v in {
            'author': self.author,
            'tags': self.tags,
            'book_id': self.book_id,
            'data_inicio': self.data_inicio,
            'data_fim': self.data_fim,
            'page': self.page,
            'per_page': self.per_page
        }.items() if v is not None}


# Classe utilitária para validações extras
class DevotionalValidator:
    """
    Classe utilitária para validações complexas.
    Implementa Single Responsibility Principle (SRP) - foco apenas em validações.
    """
    
    @staticmethod
    def validar_tags(tags: str) -> bool:
        """
        Valida formato das tags.
        Deve ser separado por vírgulas e sem caracteres especiais.
        """
        if not tags or not tags.strip():
            return False
        
        tags_list = [tag.strip() for tag in tags.split(',')]
        
        # Cada tag deve ter pelo menos 2 caracteres e só letras, números e espaços
        for tag in tags_list:
            if len(tag) < 2 or not re.match(r'^[\w\s]+$', tag):
                return False
        
        return True

    @staticmethod
    def validar_conteudo_html(conteudo: str) -> bool:
        """
        Valida se o conteúdo não contém HTML/scripts maliciosos.
        Implementa validação de segurança.
        """
        tags_perigosas = ['<script', '<iframe', '<object', '<embed', 'javascript:', 'vbscript:']
        conteudo_lower = conteudo.lower()
        
        return not any(tag in conteudo_lower for tag in tags_perigosas)

    @staticmethod
    def extrair_palavras_chave(conteudo: str, limite: int = 5) -> List[str]:
        """
        Extrai palavras-chave do conteúdo para geração automática de tags.
        Funcionalidade auxiliar para melhorar UX.
        """
        import re
        from collections import Counter
        
        # Remove pontuação e converte para minúsculas
        palavras = re.findall(r'\b[a-záêôõúí]{4,}\b', conteudo.lower())
        
        # Palavras a serem ignoradas (stopwords básicas)
        stopwords = {
            'para', 'com', 'uma', 'que', 'não', 'mais', 'como', 'pela', 'pelo',
            'este', 'esta', 'essa', 'esse', 'seus', 'suas', 'quando', 'onde',
            'porque', 'muito', 'todos', 'todas', 'sobre', 'entre', 'depois'
        }
        
        # Filtra stopwords e conta frequência
        palavras_filtradas = [p for p in palavras if p not in stopwords]
        contador = Counter(palavras_filtradas)
        
        # Retorna as palavras mais frequentes
        return [palavra for palavra, _ in contador.most_common(limite)]