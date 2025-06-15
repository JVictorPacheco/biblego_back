from app.Config.database import get_db_connection, DB_CONFIG
import bcrypt
from psycopg2 import sql
from app.Utils.database_connection import DatabaseConnection



class UsuarioRepository:
    
    def criar_usuario(self, usuario):
        
     try:
            db = get_db_connection()
            # senha_concat = usuario.email + usuario.firebase_uid
            # print(senha_concat)
            senha_hash = bcrypt.hashpw(usuario.senha.encode('utf-8') , bcrypt.gensalt())
            
            sql = """INSERT INTO usuarios
                    (nome, email, telefone, cidade, estado, endereco,
                    sexo, data_nascimento, senha, firebase_uid)
                    VALUES
                    (%(nome)s, %(email)s, %(telefone)s, %(cidade)s, %(estado)s,
                    %(endereco)s, %(sexo)s, %(data_nascimento)s, %(senha)s, %(firebase_uid)s)
                    RETURNING id"""
            
            params = {
                "nome": usuario.nome,
                "email": usuario.email,
                "telefone": usuario.telefone,
                "cidade": usuario.cidade,
                "estado": usuario.estado,
                "endereco": usuario.endereco,
                "sexo": usuario.sexo,
                "data_nascimento": usuario.data_nascimento,
                "senha": senha_hash.decode('utf-8'),
                "firebase_uid": usuario.firebase_uid
            }

            db.cursor.execute(sql, params)
            user_id = db.cursor.fetchone()[0]
            db.connection.commit()
            
            return user_id
            
     except Exception as e:
            db.connection.rollback()
            raise e
        


    def buscar_usuario_por_email(self, email):
        """Busca um usuário pelo email"""

        try:
            db = get_db_connection()
            sql = """
            SELECT id, nome, email, url_foto, endereco, sexo, 
            is_premium, data_assinatura_premium, plano_premium, 
            data_final_premium, firebase_uid, senha FROM usuarios WHERE email = %(email)s 
            """
            db.cursor.execute(sql, {'email': email})
            usuario_data = db.cursor.fetchone()

            if usuario_data:
            
             campos = [
                'id', 'nome', 'email', 'url_foto', 'endereco', 'sexo',
                'is_premium', 'data_assinatura_premium', 'plano_premium',
                'data_final_premium', 'firebase_uid', 'senha_hash'
            ]
             
             return dict(zip(campos, usuario_data))
            return None
        except Exception as e:
         print(f"Erro ao buscar usuário: {e}")
         return None



    def buscar_senha_por_email(self, email):
        """Busca APENAS o hash da senha para validação"""
        try:
            db = get_db_connection()
            db.cursor.execute(
                "SELECT senha FROM usuarios WHERE email = %(email)s",
                {'email': email}
            )
            result = db.cursor.fetchone()
            return result[0] if result else None
        except Exception as e:
            print(f"Erro ao buscar senha: {e}")
            return None
    
    
    
    def atualizar_usuario(self, user_id, novos_dados):
        
     try:
        with DatabaseConnection(**DB_CONFIG) as db:
            # 1. Prepara a atualização
            set_parts = []
            params = []
            
            for campo, valor in novos_dados.items():
                set_parts.append(f"{campo} = %s")
                params.append(valor)
            
            params.append(user_id)
            
            # 2. Query de atualização
            update_query = f"""
                UPDATE usuarios 
                SET {', '.join(set_parts)}
                WHERE id = %s
            """
            db.cursor.execute(update_query, params)
            
            # 3. Query para obter APENAS os campos alterados
            campos_alterados = list(novos_dados.keys())
            select_query = f"""
                SELECT {', '.join(campos_alterados)} 
                FROM usuarios 
                WHERE id = %s
            """
            db.cursor.execute(select_query, (user_id,))
            db.connection.commit()
            
            # 4. Processa o resultado
            resultado = db.cursor.fetchone()
            if not resultado:
                return {"Erro": "Usuário não encontrado"}, 404
            
            # 5. Monta resposta apenas com campos alterados
            dados_alterados = {
                campo: valor 
                for campo, valor in zip(campos_alterados, resultado)
                if campo != 'senha'  # Remove campo sensível se existir
            }
            
            return {
                "mensagem": "Atualização realizada com sucesso",
                "dados_alterados": dados_alterados
            }, 200
            
     except Exception as e:
        if 'db' in locals() and db.connection:
            db.connection.rollback()
        return {"erro": f"Falha na atualização: {str(e)}"}, 500
            
                     
    #@staticmethod
    def usuario_existe(user_id):
        """Verifica se um usuário existe sem trazer todos os dados"""
        try:
            with DatabaseConnection(**DB_CONFIG) as db:
                db.cursor.execute(
                    "SELECT 1 FROM usuarios WHERE id = %s LIMIT 1",
                    (user_id,)
                )
                return db.cursor.fetchone() is not None
        except Exception:
            return False



   # @staticmethod
    def deletar_usuario(user_id):
        """Deleta um usuário permanentemente"""
        try:
            with DatabaseConnection(**DB_CONFIG) as db:
                # Opção 1: DELETE físico (comum)
                db.cursor.execute(
                    "DELETE FROM usuarios WHERE id = %s RETURNING id",
                    (user_id,)
                )
                db.connection.commit()
                
                if db.cursor.rowcount == 0:
                    return {"Erro": "Usuário já removido"}, 404
                    
                return {"mensagem": "Usuário deletado com sucesso"}, 200
                
        except Exception as e:
            if 'db' in locals() and db.connection:
                db.connection.rollback()
            raise e  # Re-lança para o Service tratar
            




    def buscar_usuario_por_id(self, user_id, incluir_login_info=False):
        """Busca usuário por ID com opção de incluir informações de login"""
        try: 
            db = get_db_connection()
            
            if incluir_login_info:
                sql = """
                    SELECT id, nome, email, url_foto, endereco, sexo, 
                    is_premium, data_assinatura_premium, plano_premium, 
                    data_final_premium, primeiro_login, ultimo_login
                    FROM usuarios WHERE id = %(id)s
                """
                campos = [
                    'id', 'nome', 'email', 'url_foto', 'endereco', 'sexo',
                    'is_premium', 'data_assinatura_premium', 'plano_premium',
                    'data_final_premium', 'primeiro_login', 'ultimo_login'
                ]
            else:
                sql = """
                    SELECT id, nome, email, url_foto, endereco, sexo, 
                    is_premium, data_assinatura_premium, plano_premium, 
                    data_final_premium FROM usuarios WHERE id = %(id)s
                """
                campos = [
                    'id', 'nome', 'email', 'url_foto', 'endereco', 'sexo',
                    'is_premium', 'data_assinatura_premium', 'plano_premium',
                    'data_final_premium'
                ]
        
            db.cursor.execute(sql, {'id': user_id})
            usuario_data = db.cursor.fetchone()
            
            if usuario_data:
                usuario_dict = dict(zip(campos, usuario_data))
                
                # Converte timestamps para ISO format se incluir login info
                if incluir_login_info:
                    if usuario_dict.get('primeiro_login'):
                        usuario_dict['primeiro_login'] = usuario_dict['primeiro_login'].isoformat()
                    if usuario_dict.get('ultimo_login'):
                        usuario_dict['ultimo_login'] = usuario_dict['ultimo_login'].isoformat()
                
                return usuario_dict
            return None
            
        except Exception as e:
            print(f"Erro ao buscar usuário: {e}")
            return None
        
        
        
        
    def buscar_firebase_uid_por_email(self, email):
        """Busca APENAS o firebase_uid para geração de token"""
        try:
            db = get_db_connection()
            db.cursor.execute(
                "SELECT firebase_uid FROM usuarios WHERE email = %(email)s",
                {'email': email}
            )
            result = db.cursor.fetchone()
            return result[0] if result else None
        except Exception as e:
            print(f"Erro ao buscar firebase_uid: {e}")
            return None
                
                
                
    def buscar_usuario_por_firebase_uid(self, firebase_uid: str) -> dict:
        """Busca todos os dados do usuário pelo firebase_uid"""
        try:
            with DatabaseConnection(**DB_CONFIG) as db:
                db.cursor.execute(
                    """SELECT id, email, nome, firebase_uid 
                    FROM usuarios 
                    WHERE firebase_uid = %(firebase_uid)s""",
                    {'firebase_uid': firebase_uid}
                )
                result = db.cursor.fetchone()
                
                if not result:
                    return None
                    
                # Converte para dicionário
                return {
                    "id": result[0],
                    "email": result[1],
                    "nome": result[2],
                    "firebase_uid": result[3]
                }
                
        except Exception as e:
            print(f"Erro ao buscar usuário por firebase_uid: {e}")
            raise  # Re-lança a exceção para ser tratada no service
        
        
        
        
        
        
    def atualizar_timestamps_login(self, user_id):
        """Atualiza primeiro_login (se NULL) e ultimo_login do usuário"""
        try:
            db = get_db_connection()
            
            # Query que atualiza ambos os campos de forma inteligente
            sql = """
            UPDATE usuarios 
            SET 
                primeiro_login = CASE 
                    WHEN primeiro_login IS NULL THEN NOW() 
                    ELSE primeiro_login 
                END,
                ultimo_login = NOW()
            WHERE id = %(user_id)s
            RETURNING primeiro_login, ultimo_login
            """
            
            db.cursor.execute(sql, {'user_id': user_id})
            result = db.cursor.fetchone()
            db.connection.commit()
            
            if result:
                return {
                    'primeiro_login': result[0],
                    'ultimo_login': result[1]
                }
            return None
            
        except Exception as e:
            db.connection.rollback()
            print(f"Erro ao atualizar timestamps de login: {e}")
            raise e


    def verificar_primeiro_login(self, user_id):
        """Verifica se é o primeiro login do usuário"""
        try:
            db = get_db_connection()
            sql = "SELECT primeiro_login FROM usuarios WHERE id = %(user_id)s"
            db.cursor.execute(sql, {'user_id': user_id})
            result = db.cursor.fetchone()
            
            # Retorna True se primeiro_login é NULL (primeiro login)
            return result and result[0] is None
            
        except Exception as e:
            print(f"Erro ao verificar primeiro login: {e}")
            return False
        
    
    
    
    def buscar_info_login(self, user_id):
        """Busca informações de login do usuário"""
        try:
            db = get_db_connection()
            sql = """
            SELECT primeiro_login, ultimo_login,
                CASE 
                    WHEN primeiro_login IS NOT NULL AND ultimo_login IS NOT NULL 
                    THEN EXTRACT(EPOCH FROM (ultimo_login - primeiro_login))::integer
                    ELSE NULL 
                END as tempo_como_usuario_segundos
            FROM usuarios 
            WHERE id = %(user_id)s
            """
            
            db.cursor.execute(sql, {'user_id': user_id})
            result = db.cursor.fetchone()
            
            if result:
                return {
                    'primeiro_login': result[0],
                    'ultimo_login': result[1], 
                    'tempo_como_usuario_segundos': result[2],
                    'tem_login_anterior': result[0] is not None
                }
            return None
            
        except Exception as e:
            print(f"Erro ao buscar info de login: {e}")
            return None


    def buscar_estatisticas_login_geral(self):
        """Busca estatísticas gerais de login para analytics"""
        try:
            db = get_db_connection()
            sql = """
            SELECT 
                COUNT(*) as total_usuarios,
                COUNT(primeiro_login) as usuarios_com_login,
                COUNT(CASE WHEN primeiro_login >= CURRENT_DATE THEN 1 END) as primeiros_logins_hoje,
                COUNT(CASE WHEN ultimo_login >= CURRENT_DATE THEN 1 END) as logins_hoje,
                COUNT(CASE WHEN ultimo_login >= CURRENT_DATE - INTERVAL '7 days' THEN 1 END) as logins_semana
            FROM usuarios
            """
            
            db.cursor.execute(sql)
            result = db.cursor.fetchone()
            
            if result:
                return {
                    'total_usuarios': result[0],
                    'usuarios_com_login': result[1],
                    'primeiros_logins_hoje': result[2],
                    'logins_hoje': result[3],
                    'logins_ultima_semana': result[4]
                }
            return None
            
        except Exception as e:
            print(f"Erro ao buscar estatísticas de login: {e}")
            return None