import jwt
from datetime import datetime, timedelta
from app.Models.usuario import Usuario
from app.Repository.usuario_repository import UsuarioRepository
from werkzeug.exceptions import BadRequest, Unauthorized
import bcrypt


class AuthService:
    def __init__(self):
        self.usuario_repository = UsuarioRepository()
        self.secret_key = "pythonjwt"
        self.algorithm = "HS256"


    def login(self, email, senha):
        """Lógica principal de autenticação"""
        # 1. Validação das credenciais
        senha_hash = self.usuario_repository.buscar_senha_por_email(email)
        if not senha_hash or not self._validar_senha(senha, senha_hash):
            raise Unauthorized("Email ou senha incorretos")

        # 2. Busca dados do usuário
        usuario = self.usuario_repository.buscar_usuario_por_email(email)
        if not usuario:
            raise Unauthorized("Usuário não encontrado")

        # 3. Gera token JWT
        token = self.gerar_token(usuario['id'])

        return {
            "token": token,
            "usuario": usuario
        }



    def _validar_senha(self, senha_fornecida, senha_hash):
        """Validação encapsulada da senha"""
        try:
            return bcrypt.checkpw(
                senha_fornecida.encode('utf-8'),
                senha_hash.encode('utf-8')
            )
        except Exception as e:
            print(f"Erro na validação de senha: {e}")
            return False



    def gerar_token(self, usuario_id):
        """Geração de token JWT"""
        payload = {
            "usuario_id": usuario_id,
            "exp": datetime.utcnow() + timedelta(hours=2)
        }
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
    
    
    
    def verificar_token(self, token):
        """Verifica se o token JWT é válido e retorna o payload"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except jwt.ExpiredSignatureError:
            print("Token expirado")
            return None
        except jwt.InvalidTokenError:
            print("Token inválido")
            return None
        
        
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    # def __init__(self):
    #     self.usuario_repository = UsuarioRepository()
    #     self.secret_key = 'pythonjwt'
    #     self.algorithm = "HS256"

    # def autenticar_usuario(self, email, senha):
    #     """Autenticar o usuario e retorna um token JWT se válido."""
    #     usuario = self.usuario_repository.buscar_usuario_por_email(email)
    #     if not usuario:
    #         return None # Se o usuario não for encontrado
        
    #     # Verifica senha
    #     if not usuario.verificar_senha(senha):
    #         return None
        
    #     # Gerar o token JWT
    #     token = self.gerar_token(usuario.id)
    #     return token
    
    # def gerar_token(self, usuario_id):
    #     """Gera um token JWT para usuário"""
    #     payload = {
    #         "usuario_id": usuario_id,
    #         "exp": datetime.utcnow() + timedelta(hours=2)
    #     }
    #     token = jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
    #     return token
    
    
    # def verificar_token(self, token):
    #     """Verifica se o token JWT é válido"""

    #     try:
    #         payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
    #         return payload
    #     except jwt.ExpiredSignatureError:
    #         return None
    #     except jwt.InvalidAlgorithmError:
    #         return None

