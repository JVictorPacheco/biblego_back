import jwt
from datetime import datetime, timedelta
from app.Models.usuario import Usuario
from app.Service.token_service import TokenService
from app.Repository.usuario_repository import UsuarioRepository
from werkzeug.exceptions import Unauthorized
import bcrypt


class AuthService:
    def __init__(self):
        self.token_service = TokenService()
        self.usuario_repo = UsuarioRepository()



    def login(self, email, senha):
        
        """Autentica usuário e retorna token"""
        usuario = self.validar_credenciais(email, senha)
        token = self.token_service.gerar_token(usuario['email'], usuario['firebase_uid'])
        
        return {
            
            "token": token,
            "Mensagem": "Login realizado com sucesso",
            "usuario": {  # Retorna diretamente o dict
            "id": usuario["id"],
            "email": usuario["email"],
            "nome": usuario.get("nome"),
            "firebase_uid": usuario["firebase_uid"]
            # Adicione outros campos necessários
            }
        }
        
        
        
    def validar_credenciais(self, email: str, senha: str):
        """Valida email e senha"""
        usuario = self.usuario_repo.buscar_usuario_por_email(email)
        
        if not usuario:
           raise Unauthorized("Credenciais inválidos")
       
        senha_hash = usuario.get('senha_hash') or usuario.get('senha')
        if not senha_hash or not self._validar_senha(senha, senha_hash):
         raise Unauthorized("Credenciais inválidas")
    
        return usuario



    def _validar_senha(self, senha: str, senha_hash: str) -> bool:
        return bcrypt.checkpw(senha.encode('utf-8'), senha_hash.encode('utf-8'))
        
        



    def obter_usuario_por_token(self, token: str) -> dict:
        """Obtém usuário completo a partir do token JWT"""
        payload = self.token_service.obter_identidade_usuario(token)
        usuario = self.usuario_repo.buscar_usuario_por_firebase_uid(payload["firebase_uid"])
        if not usuario:
            raise Unauthorized("Usuário não encontrado")
        return usuario        
            

        


