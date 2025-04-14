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
            data_final_premium FROM usuarios WHERE email = %(email)s 
            """
            db.cursor.execute(sql, {'email': email})
            usuario_data = db.cursor.fetchone()

            if usuario_data:
            
             campos = [
                'id', 'nome', 'email', 'url_foto', 'endereco', 'sexo',
                'is_premium', 'data_assinatura_premium', 'plano_premium',
                'data_final_premium'
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
            




    def buscar_usuario_por_id(self, user_id):
        """Buscando usuario por id"""
        
        try: 
            db = get_db_connection()
            sql =     """
                SELECT id, nome, email, url_foto, endereco, sexo, 
                is_premium, data_assinatura_premium, plano_premium, 
                data_final_premium FROM usuarios WHERE id = %(id)s
                      """
        
            db.cursor.execute(sql, {'id': user_id})
            usuario_data = db.cursor.fetchone()
            
            if usuario_data:
                
                
                campos = [
                'id', 'nome', 'email', 'url_foto', 'endereco', 'sexo',
                'is_premium', 'data_assinatura_premium', 'plano_premium',
                'data_final_premium'
            ]
                
                return dict(zip(campos, usuario_data))
            return None
        except Exception as e:
            print(f"Erro ao buscar usuário: {e}")
            return None
                
                
                