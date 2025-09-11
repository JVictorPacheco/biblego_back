from typing import Optional, List, Dict, Any
from datetime import date, datetime
from flask import jsonify, request
import psycopg2
from psycopg2.extras import RealDictCursor
from app.Config.production_database import get_db_connection, get_db_config
from app.Utils.database_connection import DatabaseConnection


class DevotionalsRepository:
    """
    Repository responsável pelas operações de banco de dados relacionadas aos devocionais.
    Implementa o padrão Repository seguindo princípios SOLID e Clean Code.
    """

    @staticmethod
    def criar_devocional(devocional_data: Dict[str, Any]) -> Optional[int]:
        """
        Cria um novo devocional no banco de dados (versão com debug)
        """
        try:
            # DEBUG - verificar dados recebidos
            print(f"[REPO DEBUG] Dados recebidos: {devocional_data}")
            print(f"[REPO DEBUG] Tipo dos dados: {type(devocional_data)}")
            
            if devocional_data is None:
                print("[REPO DEBUG] devocional_data é None")
                raise ValueError("Dados do devocional são None")
            
            if not isinstance(devocional_data, dict):
                print(f"[REPO DEBUG] Dados não são dict: {type(devocional_data)}")
                raise ValueError("Dados devem ser um dicionário")
            
            # Validação de campos obrigatórios
            campos_obrigatorios = [
                'title', 'main_verse', 'verse_reference', 'book_id',
                'chapter', 'verse', 'content', 'application',
                'prayer', 'author', 'publish_date', 'tags'
            ]
            
            campos_faltando = []
            for campo in campos_obrigatorios:
                if campo not in devocional_data:
                    campos_faltando.append(campo)
            
            if campos_faltando:
                print(f"[REPO DEBUG] Campos faltando: {campos_faltando}")
                raise ValueError(f"Campos obrigatórios faltando: {', '.join(campos_faltando)}")
            
            print(f"[REPO DEBUG] Todos os campos presentes: {list(devocional_data.keys())}")
            
            # Executar insert no banco
            with DatabaseConnection(**get_db_config()) as db:
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
                
                print(f"[REPO DEBUG] Executando query...")
                print(f"[REPO DEBUG] Valores: {devocional_data}")
                
                db.cursor.execute(query, devocional_data)
                
                result = db.cursor.fetchone()
                if not result:
                    print("[REPO DEBUG] Nenhum resultado retornado")
                    raise Exception("Nenhum ID retornado pelo banco de dados")
                
                devocional_id = result[0]
                db.connection.commit()
                
                print(f"[REPO DEBUG] Devocional criado com ID: {devocional_id}")
                return devocional_id
                
        except psycopg2.Error as e:
            print(f"[REPO DEBUG] Erro de banco: {e}")
            print(f"[REPO DEBUG] Código do erro: {e.pgcode}")
            print(f"[REPO DEBUG] Dados que causaram erro: {devocional_data}")
            if 'db' in locals() and db.connection:
                db.connection.rollback()
            raise Exception(f"Erro de banco de dados: {str(e)}")
        except Exception as e:
            print(f"[REPO DEBUG] Erro inesperado: {e}")
            print(f"[REPO DEBUG] Tipo do erro: {type(e)}")
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
            with DatabaseConnection(**get_db_config()) as db:
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
            with DatabaseConnection(**get_db_config()) as db:
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
            with DatabaseConnection(**get_db_config()) as db:
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
            with DatabaseConnection(**get_db_config()) as db:
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
            with DatabaseConnection(**get_db_config()) as db:
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
            with DatabaseConnection(**get_db_config()) as db:
                query = """
                    SELECT id, title, main_verse, verse_reference, book_id,
                           chapter, verse, content, application, prayer,
                           author, publish_date, tags
                    FROM devotionals_flow
                    WHERE publish_date = current_date  
                    ORDER BY id DESC
                    LIMIT 1
                """
                
                #%(publish_date)s
                
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
            with DatabaseConnection(**get_db_config()) as db:
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
            with DatabaseConnection(**get_db_config()) as db:
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
        """Deleta um devocional no banco (VERSÃO SIMPLES)"""
        try:
            with DatabaseConnection(**get_db_config()) as db:
                query = "DELETE FROM devotionals_flow WHERE id = %(id)s"
                db.cursor.execute(query, {'id': devocional_id})
                db.connection.commit()
                return db.cursor.rowcount > 0
        except Exception as e:
            print(f"Erro ao deletar devocional: {e}")
            return False

    @staticmethod
    def buscar_devocional_mais_recente_ate_hoje() -> Optional[Dict[str, Any]]:
        """Busca o devocional mais recente até hoje (SEM datas futuras)"""
        try:
            from datetime import date
            
            with DatabaseConnection(**get_db_config()) as db:
                hoje = date.today()
                
                query = """
                    SELECT id, title, main_verse, verse_reference, book_id,
                        chapter, verse, content, application, prayer,
                        author, publish_date, tags
                    FROM devotionals_flow
                    WHERE publish_date <= %(hoje)s
                    ORDER BY publish_date DESC, id DESC
                    LIMIT 1
                """
                
                db.cursor.execute(query, {'hoje': hoje})
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
            print(f"Erro ao buscar devocional mais recente até hoje: {e}")
            return None


    @staticmethod
    def buscar_devocional_periodo_ate_hoje(dias_anteriores: int = 7) -> List[Dict[str, Any]]:
        """Busca devocionais em período até hoje"""
        try:
            from datetime import date, timedelta
            
            with DatabaseConnection(**get_db_config()) as db:
                hoje = date.today()
                data_inicio = hoje - timedelta(days=dias_anteriores)
                
                query = """
                    SELECT id, title, main_verse, verse_reference, book_id,
                        chapter, verse, content, application, prayer,
                        author, publish_date, tags
                    FROM devotionals_flow
                    WHERE publish_date BETWEEN %(data_inicio)s AND %(hoje)s
                    ORDER BY publish_date DESC, id DESC
                """
                
                db.cursor.execute(query, {
                    'data_inicio': data_inicio,
                    'hoje': hoje
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
    def buscar_por_criterios_dev(titulo: str = "", autor: str = "") -> List[Dict[str, Any]]:
        """
        Busca devocionais por critérios (para desenvolvimento)
        Args:
            titulo: Parte do título para buscar
            autor: Parte do nome do autor para buscar
        Returns:
            Lista de devocionais encontrados
        """
        try:
            with DatabaseConnection(**get_db_config()) as db:
                # Construir query dinamicamente baseada nos critérios
                where_conditions = []
                params = {}
                
                if titulo.strip():
                    where_conditions.append("LOWER(title) LIKE LOWER(%(titulo)s)")
                    params['titulo'] = f"%{titulo.strip()}%"
                
                if autor.strip():
                    where_conditions.append("LOWER(author) LIKE LOWER(%(autor)s)")
                    params['autor'] = f"%{autor.strip()}%"
                
                # Se não tem critérios, retorna lista vazia
                if not where_conditions:
                    print("[REPO DEBUG] Nenhum critério fornecido")
                    return []
                
                # Query base
                query = """
                    SELECT id, title, main_verse, verse_reference, book_id,
                        chapter, verse, content, application, prayer,
                        author, publish_date, tags
                    FROM devotionals_flow
                    WHERE {}
                    ORDER BY publish_date DESC, id DESC
                    LIMIT 20
                """.format(" AND ".join(where_conditions))
                
                print(f"[REPO DEBUG] Query: {query}")
                print(f"[REPO DEBUG] Params: {params}")
                
                db.cursor.execute(query, params)
                resultados = db.cursor.fetchall()
                
                if not resultados:
                    print("[REPO DEBUG] Nenhum resultado encontrado")
                    return []
                
                # Converter para lista de dicionários
                campos = [
                    'id', 'title', 'main_verse', 'verse_reference', 'book_id',
                    'chapter', 'verse', 'content', 'application', 'prayer',
                    'author', 'publish_date', 'tags'
                ]
                
                devocionais = []
                for resultado in resultados:
                    devocional_dict = dict(zip(campos, resultado))
                    devocionais.append(devocional_dict)
                
                print(f"[REPO DEBUG] Encontrados {len(devocionais)} devocionais")
                return devocionais
                
        except Exception as e:
            print(f"[REPO DEBUG] Erro na busca: {e}")
            return []

   

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
            with DatabaseConnection(**get_db_config()) as db:
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