import jwt
from datetime import datetime, timedelta
from app.Models.usuario import Usuario
from app.Repository.usuario_repository import UsuarioRepository


class AuthService:
    
    def __init__(self):
        self.usuario_reporsitory = UsuarioRepository()
        self.secret_key = "pythonjwt"
        self.algorithm = "HS256"

    def autenticar_usuario(self, email, senha):
        """Autenticar o usuario e retorna um token JWT se válido."""
        usuario = self.usuario_reporsitory.buscar_usuario_por_email(email)
        if not usuario:
            return None # Se o usuario não for encontrado
        
        # Verifica senha
        if not usuario.verificar_senha(senha):
            return None
        
        # Gerar o token JWT
        token = self.gerar_token(usuario.id)
        return token
    
    def gerar_token(self, usuario_id):
        """Gera um token JWT para usuário"""
        payload = {
            "usuario_id": usuario_id,
            "exp": datetime.utcnow() + timedelta(hours=2)
        }
        token = jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
        return token
    
    
    def verificar_token(self, token):
        """Verifica se o token JWT é válido"""

        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidAlgorithmError:
            return None

