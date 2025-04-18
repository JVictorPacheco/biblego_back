import jwt
from datetime import datetime, timedelta
from app.Core.security_config import SecurityConfig




class TokenService:
    
    def __init__(self):
        self.secret_key = SecurityConfig.SECRET_KEY
        self.algorithm = SecurityConfig.ALGORITHM

    
    
    def gerar_token(self, email: str, firebase_uid: str) -> str:
        """Gera um token JWT contendo apenas email e firebase_uid"""
        payload = {
            "email": email,
            "firebase_uid": firebase_uid,
            "expiration": datetime.utcnow() + timedelta(hours=SecurityConfig.TOKEN_EXPIRE_HOURS)
        }
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
    
    
    def verificar_token(self, token: str) -> dict:
        """Valida o token e retorna o payload"""
        try:
            return jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
        except (jwt.ExpiredSignatureError, jwt.InvalidTokenError) as e:
            raise ValueError(f"Token inválido: {str(e)}")



    def get_token_payload(self):
        """Retorna os dados necessários para o payload do token"""
        if not self.email or not self.firebase_uid:
            raise ValueError("Email e firebase_uid são obrigatórios para gerar o token")
        return {
            "email": self.email,
            "firebase_uid": self.firebase_uid
        }
        
        
        
    def obter_identidade_usuario(self, token: str) -> dict:
        """Obtém a identidade do usuário a partir do token"""
        payload = self.verificar_token(token)
        return {
            "email": payload["email"],
            "firebase_uid": payload["firebase_uid"]
    }