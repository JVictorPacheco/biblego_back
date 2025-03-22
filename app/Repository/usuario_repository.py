from app.Config.database import get_db_connection
from app.Models.usuario import Usuario
import bcrypt


class UsuarioRepository:
    
    def criar_usuario(self, usuario):
        print("criar_usuario -> ", usuario)
        try:
            db = get_db_connection()

            senha_hash = bcrypt.hashpw(usuario.senha.encode('utf-8'), bcrypt.gensalt())


            sql = """INSERT INTO usuarios
                    (nome, email, telefone, cidade, estado, endereco, is_premium,
                    data_assinatura_premium, plano_premium, data_final_premium, idade,
                    sexo, data_nascimento, status_conta, notificacao_habilitada,
                    termos_aceitos, cod_verificacao, url_foto, senha)
                    VALUES (%(nome)s, %(email)s, %(telefone)s, %(cidade)s, %(estado)s, 
                    %(endereco)s, %(is_premium)s, %(data_assinatura_premium)s, 
                    %(plano_premium)s, %(data_final_premium)s, %(idade)s, %(sexo)s, 
                    %(data_nascimento)s, %(status_conta)s, %(notificacao_habilitada)s,
                    %(termos_aceitos)s, %(cod_verificacao)s, %(url_foto)s, %(senha)s)"""
            
            # """INSERT INTO usuario 
            #         (nome, email, telefone, cidade, estado, endereco, is_premium, 
            #          data_assinatura_premium, plano_premium, data_final_premium, idade, 
            #          sexo, data_nascimento, status_conta, notificacao_habilitada, 
            #          termos_aceitos, cod_verificacao, url_foto, senha) 
            #          VALUES (:nome, :email, :telefone, :cidade, :estado, :endereco, :is_premium, :data_assinatura_premium, :plano_premium, :data_final_premium, :idade, :sexo, :data_nascimento, :status_conta, :notificacao_habilitada, :termos_aceitos, :cod_verificacao, :url_foto, :senha)"""

            params = {
                "nome": usuario.nome, "email": usuario.email, "telefone": usuario.telefone,
                "cidade": usuario.cidade, "estado": usuario.estado, "endereco": usuario.endereco,
                "is_premium": usuario.is_premium, "data_assinatura_premium": usuario.data_assinatura_premium,
                "plano_premium": usuario.plano_premium, "data_final_premium": usuario.data_final_premium,
                "idade": usuario.idade, "sexo": usuario.sexo, "data_nascimento": usuario.data_nascimento,
                "status_conta": usuario.status_conta, "notificacao_habilitada": usuario.notificacao_habilitada,
                "termos_aceitos": usuario.termos_aceitos, "cod_verificacao": usuario.cod_verificacao,
                "url_foto": usuario.url_foto, "senha": senha_hash.decode('utf-8') #usuario.senha
}

            db.cursor.execute(sql, params)  # Substitua db.session.execute por db.cursor.execute
            db.connection.commit()  # Commit correto
            return None  # Retorno explícito para sucesso

        except Exception as e:
            db.connection.rollback()
            return {"erro": str(e)}, 500
        



    def buscar_usuario_por_email(self, email):
        """Busca um usuário pelo email"""

        try:
            db = get_db_connection()
            sql = "SELECT * FROM usuarios WHERE email = %(emails)s"
            db.cursor.execute(sql, {'email': email})
            usuario_data = db.cursor.fetchone()
            if usuario_data:
                 return Usuario(**usuario_data) # Criando uma instancia de Usuario
            return None
        
        except Exception as e:
            return {"erro": str(e)}, 500


    
        
    




    


    