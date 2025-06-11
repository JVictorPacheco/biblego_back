from typing import Optional, List, Dict, Any
from datetime import date, datetime
import psycopg2
from psycopg2.extras import RealDictCursor
from app.Config.database import get_db_connection, DB_CONFIG
from app.Utils.database_connection import DatabaseConnection


class DevotionalsRepository:
    """
    Repository responsável pelas operações de banco de dados relacionadas aos devocionais.
    Implementa o padrão Repository seguindo princípios SOLID e Clean Code.
    """

    @staticmethod
    def criar_devocional(devocional_data: Dict[str, Any]) -> Optional[int]:
        """
        Cria um novo devocional no banco de dados
        
        Args:
            devocional_data: Dicionário com os dados do devocional
            
        Returns:
            ID do devocional criado ou None em caso de erro
            
        Raises:
            ValueError: Se dados obrigatórios estiverem ausentes
            Exception: Erros de banco de dados
        """
        try:
            with DatabaseConnection(**DB_CONFIG) as db:
                query = """
                    INSERT INTO devotionals_flow (
                        title, main_verse, verse_reference, book_id, 
                        chapter, verse, content, application, 
                        prayer, author, publish_date, tags
                    ) VALUES (
                        %(title)s, %(main_verse)s, %(verse_reference)s, %(book_id)s,
                        %(chapter)s, %(verse)s, %(content)s, %(application)s,
                        %(prayer)s, %(author)s, %(publish_date)s, %(tags)s
                    ) RETURNING id
                """
                
                db.cursor.execute(query, devocional_data)
                devocional_id = db.cursor.fetchone()[0]
                db.connection.commit()
                
                return devocional_id
                
        except psycopg2.Error as e:
            print(f"Erro de banco ao criar devocional: {e}")
            if 'db' in locals() and db.connection:
                db.connection.rollback()
            raise
        except Exception as e:
            print(f"Erro inesperado ao criar devocional: {e}")
            if 'db' in locals() and db.connection:
                db.connection.rollback()
            raise

    @staticmethod
    def buscar_devocional_por_id(devocional_id: int) -> Optional[Dict[str, Any]]:
        """
        Busca um devocional específico pelo ID
        
        Args:
            devocional_id: ID do devocional
            
        Returns:
            Dicionário com dados do devocional ou None se não encontrado
        """
        try:
            with DatabaseConnection(**DB_CONFIG) as db:
                query = """
                    SELECT id, title, main_verse, verse_reference, book_id,
                           chapter, verse, content, application, prayer,
                           author, publish_date, tags
                    FROM devotionals_flow
                    WHERE id = %(id)s
                """
                
                db.cursor.execute(query, {'id': devocional_id})
                result = db.cursor.fetchone()
                
                if result:
                    campos = [
                        'id', 'title', 'main_verse', 'verse_reference', 'book_id',
                        'chapter', 'verse', 'content', 'application', 'prayer',
                        'author', 'publish_date', 'tags'
                    ]
                    return dict(zip(campos, result))
                
                return None
                
        except Exception as e:
            print(f"Erro ao buscar devocional por ID: {e}")
            return None

    @staticmethod
    def buscar_devocionais_por_data(data_publicacao: date) -> List[Dict[str, Any]]:
        """
        Busca devocionais por data de publicação
        
        Args:
            data_publicacao: Data de publicação
            
        Returns:
            Lista de devocionais da data especificada
        """
        try:
            with DatabaseConnection(**DB_CONFIG) as db:
                query = """
                    SELECT id, title, main_verse, verse_reference, book_id,
                           chapter, verse, content, application, prayer,
                           author, publish_date, tags
                    FROM devotionals_flow
                    WHERE publish_date = %(publish_date)s
                    ORDER BY id DESC
                """
                
                db.cursor.execute(query, {'publish_date': data_publicacao})
                results = db.cursor.fetchall()
                
                campos = [
                    'id', 'title', 'main_verse', 'verse_reference', 'book_id',
                    'chapter', 'verse', 'content', 'application', 'prayer',
                    'author', 'publish_date', 'tags'
                ]
                
                return [dict(zip(campos, row)) for row in results]
                
        except Exception as e:
            print(f"Erro ao buscar devocionais por data: {e}")
            return []

    @staticmethod
    def buscar_devocionais_por_periodo(data_inicio: date, data_fim: date) -> List[Dict[str, Any]]:
        """
        Busca devocionais dentro de um período específico
        
        Args:
            data_inicio: Data de início do período
            data_fim: Data de fim do período
            
        Returns:
            Lista de devocionais no período especificado
        """
        try:
            with DatabaseConnection(**DB_CONFIG) as db:
                query = """
                    SELECT id, title, main_verse, verse_reference, book_id,
                           chapter, verse, content, application, prayer,
                           author, publish_date, tags
                    FROM devotionals_flow
                    WHERE publish_date BETWEEN %(data_inicio)s AND %(data_fim)s
                    ORDER BY publish_date DESC, id DESC
                """
                
                db.cursor.execute(query, {
                    'data_inicio': data_inicio,
                    'data_fim': data_fim
                })
                results = db.cursor.fetchall()
                
                campos = [
                    'id', 'title', 'main_verse', 'verse_reference', 'book_id',
                    'chapter', 'verse', 'content', 'application', 'prayer',
                    'author', 'publish_date', 'tags'
                ]
                
                return [dict(zip(campos, row)) for row in results]
                
        except Exception as e:
            print(f"Erro ao buscar devocionais por período: {e}")
            return []

    @staticmethod
    def buscar_devocionais_por_autor(autor: str, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Busca devocionais de um autor específico
        
        Args:
            autor: Nome do autor
            limit: Limite de resultados (padrão: 50)
            
        Returns:
            Lista de devocionais do autor especificado
        """
        try:
            with DatabaseConnection(**DB_CONFIG) as db:
                query = """
                    SELECT id, title, main_verse, verse_reference, book_id,
                           chapter, verse, content, application, prayer,
                           author, publish_date, tags
                    FROM devotionals_flow
                    WHERE author ILIKE %(autor)s
                    ORDER BY publish_date DESC, id DESC
                    LIMIT %(limit)s
                """
                
                db.cursor.execute(query, {
                    'autor': f'%{autor}%',
                    'limit': limit
                })
                results = db.cursor.fetchall()
                
                campos = [
                    'id', 'title', 'main_verse', 'verse_reference', 'book_id',
                    'chapter', 'verse', 'content', 'application', 'prayer',
                    'author', 'publish_date', 'tags'
                ]
                
                return [dict(zip(campos, row)) for row in results]
                
        except Exception as e:
            print(f"Erro ao buscar devocionais por autor: {e}")
            return []

    @staticmethod
    def buscar_devocionais_por_tags(tags: str, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Busca devocionais que contenham as tags especificadas
        
        Args:
            tags: Tags para buscar (separadas por vírgula)
            limit: Limite de resultados (padrão: 50)
            
        Returns:
            Lista de devocionais que contenham as tags
        """
        try:
            with DatabaseConnection(**DB_CONFIG) as db:
                query = """
                    SELECT id, title, main_verse, verse_reference, book_id,
                           chapter, verse, content, application, prayer,
                           author, publish_date, tags
                    FROM devotionals_flow
                    WHERE tags ILIKE %(tags)s
                    ORDER BY publish_date DESC, id DESC
                    LIMIT %(limit)s
                """
                
                db.cursor.execute(query, {
                    'tags': f'%{tags}%',
                    'limit': limit
                })
                results = db.cursor.fetchall()
                
                campos = [
                    'id', 'title', 'main_verse', 'verse_reference', 'book_id',
                    'chapter', 'verse', 'content', 'application', 'prayer',
                    'author', 'publish_date', 'tags'
                ]
                
                return [dict(zip(campos, row)) for row in results]
                
        except Exception as e:
            print(f"Erro ao buscar devocionais por tags: {e}")
            return []

    @staticmethod
    def buscar_devocional_do_dia(data_referencia: date = None) -> Optional[Dict[str, Any]]:
        """
        Busca o devocional do dia específico (se data_referencia for None, usa hoje)
        
        Args:
            data_referencia: Data de referência (opcional, padrão: hoje)
            
        Returns:
            Devocional do dia ou None se não encontrado
        """
        if data_referencia is None:
            data_referencia = date.today()
            
        try:
            with DatabaseConnection(**DB_CONFIG) as db:
                query = """
                    SELECT id, title, main_verse, verse_reference, book_id,
                           chapter, verse, content, application, prayer,
                           author, publish_date, tags
                    FROM devotionals_flow
                    WHERE publish_date = %(publish_date)s
                    ORDER BY id DESC
                    LIMIT 1
                """
                
                db.cursor.execute(query, {'publish_date': data_referencia})
                result = db.cursor.fetchone()
                
                if result:
                    campos = [
                        'id', 'title', 'main_verse', 'verse_reference', 'book_id',
                        'chapter', 'verse', 'content', 'application', 'prayer',
                        'author', 'publish_date', 'tags'
                    ]
                    return dict(zip(campos, result))
                
                return None
                
        except Exception as e:
            print(f"Erro ao buscar devocional do dia: {e}")
            return None

    @staticmethod
    def listar_devocionais_paginado(page: int = 1, per_page: int = 10) -> Dict[str, Any]:
        """
        Lista devocionais com paginação
        
        Args:
            page: Número da página (padrão: 1)
            per_page: Itens por página (padrão: 10)
            
        Returns:
            Dicionário com devocionais e informações de paginação
        """
        try:
            with DatabaseConnection(**DB_CONFIG) as db:
                # Calcula offset
                offset = (page - 1) * per_page
                
                # Query para contar total de registros
                count_query = "SELECT COUNT(*) FROM devotionals_flow"
                db.cursor.execute(count_query)
                total_count = db.cursor.fetchone()[0]
                
                # Query para buscar registros paginados
                query = """
                    SELECT id, title, main_verse, verse_reference, book_id,
                           chapter, verse, content, application, prayer,
                           author, publish_date, tags
                    FROM devotionals_flow
                    ORDER BY publish_date DESC, id DESC
                    LIMIT %(per_page)s OFFSET %(offset)s
                """
                
                db.cursor.execute(query, {
                    'per_page': per_page,
                    'offset': offset
                })
                results = db.cursor.fetchall()
                
                campos = [
                    'id', 'title', 'main_verse', 'verse_reference', 'book_id',
                    'chapter', 'verse', 'content', 'application', 'prayer',
                    'author', 'publish_date', 'tags'
                ]
                
                devocionais = [dict(zip(campos, row)) for row in results]
                
                # Calcula informações de paginação
                total_pages = (total_count + per_page - 1) // per_page
                has_next = page < total_pages
                has_prev = page > 1
                
                return {
                    'devocionais': devocionais,
                    'pagination': {
                        'page': page,
                        'per_page': per_page,
                        'total': total_count,
                        'total_pages': total_pages,
                        'has_next': has_next,
                        'has_prev': has_prev
                    }
                }
                
        except Exception as e:
            print(f"Erro ao listar devocionais paginados: {e}")
            return {
                'devocionais': [],
                'pagination': {
                    'page': page,
                    'per_page': per_page,
                    'total': 0,
                    'total_pages': 0,
                    'has_next': False,
                    'has_prev': False
                }
            }

    @staticmethod
    def atualizar_devocional(devocional_id: int, novos_dados: Dict[str, Any]) -> bool:
        """
        Atualiza um devocional existente
        
        Args:
            devocional_id: ID do devocional a ser atualizado
            novos_dados: Dicionário com os campos a serem atualizados
            
        Returns:
            True se atualizado com sucesso, False caso contrário
        """
        try:
            with DatabaseConnection(**DB_CONFIG) as db:
                # Prepara a atualização dinâmica
                set_parts = []
                params = {'id': devocional_id}
                
                campos_permitidos = {
                    'title', 'main_verse', 'verse_reference', 'book_id',
                    'chapter', 'verse', 'content', 'application',
                    'prayer', 'author', 'publish_date', 'tags'
                }
                
                for campo, valor in novos_dados.items():
                    if campo in campos_permitidos:
                        set_parts.append(f"{campo} = %({campo})s")
                        params[campo] = valor
                
                if not set_parts:
                    return False
                
                query = f"""
                    UPDATE devotionals_flow 
                    SET {', '.join(set_parts)}
                    WHERE id = %(id)s
                """
                
                db.cursor.execute(query, params)
                db.connection.commit()
                
                return db.cursor.rowcount > 0
                
        except Exception as e:
            print(f"Erro ao atualizar devocional: {e}")
            if 'db' in locals() and db.connection:
                db.connection.rollback()
            return False

    @staticmethod
    def deletar_devocional(devocional_id: int) -> bool:
        """
        Deleta um devocional
        
        Args:
            devocional_id: ID do devocional a ser deletado
            
        Returns:
            True se deletado com sucesso, False caso contrário
        """
        try:
            with DatabaseConnection(**DB_CONFIG) as db:
                query = "DELETE FROM devotionals_flow WHERE id = %(id)s"
                
                db.cursor.execute(query, {'id': devocional_id})
                db.connection.commit()
                
                return db.cursor.rowcount > 0
                
        except Exception as e:
            print(f"Erro ao deletar devocional: {e}")
            if 'db' in locals() and db.connection:
                db.connection.rollback()
            return False

    @staticmethod
    def devocional_existe(devocional_id: int) -> bool:
        """
        Verifica se um devocional existe
        
        Args:
            devocional_id: ID do devocional
            
        Returns:
            True se existe, False caso contrário
        """
        try:
            with DatabaseConnection(**DB_CONFIG) as db:
                query = "SELECT 1 FROM devotionals_flow WHERE id = %(id)s LIMIT 1"
                
                db.cursor.execute(query, {'id': devocional_id})
                result = db.cursor.fetchone()
                
                return result is not None
                
        except Exception as e:
            print(f"Erro ao verificar existência do devocional: {e}")
            return False

    @staticmethod
    def buscar_devocionais_por_livro(book_id: int, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Busca devocionais de um livro bíblico específico
        
        Args:
            book_id: ID do livro bíblico
            limit: Limite de resultados (padrão: 50)
            
        Returns:
            Lista de devocionais do livro especificado
        """
        try:
            with DatabaseConnection(**DB_CONFIG) as db:
                query = """
                    SELECT id, title, main_verse, verse_reference, book_id,
                           chapter, verse, content, application, prayer,
                           author, publish_date, tags
                    FROM devotionals_flow
                    WHERE book_id = %(book_id)s
                    ORDER BY chapter, verse, publish_date DESC
                    LIMIT %(limit)s
                """
                
                db.cursor.execute(query, {
                    'book_id': book_id,
                    'limit': limit
                })
                results = db.cursor.fetchall()
                
                campos = [
                    'id', 'title', 'main_verse', 'verse_reference', 'book_id',
                    'chapter', 'verse', 'content', 'application', 'prayer',
                    'author', 'publish_date', 'tags'
                ]
                
                return [dict(zip(campos, row)) for row in results]
                
        except Exception as e:
            print(f"Erro ao buscar devocionais por livro: {e}")
            return []