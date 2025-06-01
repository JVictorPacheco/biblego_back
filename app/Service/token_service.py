import jwt
from datetime import datetime, timedelta, timezone
from app.Core.security_config import SecurityConfig
from datetime import datetime, timezone  # Adicione timezone
from typing import Tuple, Optional
import uuid
from typing import Optional, Dict, Any
import json
from app.Config.database import get_db_connection
from flask import request
from app.Repository.token_audit_repository import TokenAuditRepository
from app.Models.token_audit import TokenAuditCreate



class TokenService:
    
    def __init__(self):
        self.secret_key = SecurityConfig.SECRET_KEY
        self.algorithm = SecurityConfig.ALGORITHM
        # Lembrar que em produção tenho que considerar injetar uma dependencia para auditoria
        self.audit_repository = TokenAuditRepository()





    def _audit_token(self, user_id: str, token_type: str, action: str, 
                    token_jti: str = None, error: str = None, 
                   additional_data: Optional[Dict[str, Any]] = None):
        """Registra ação de token para auditoria"""
        if not SecurityConfig.TOKEN_AUDIT_ENABLED:
            return
            
        audit_data = TokenAuditCreate(
            user_id=user_id,
            token_type=token_type,
            action=action,
            token_jti=token_jti,
            error=error,
            ip_address=request.remote_addr if request else None,
            user_agent=request.headers.get('User-Agent') if request else None,
            additional_data=additional_data
        )
        
        self.audit_repository.create(audit_data)


    
    
    def gerar_tokens(self, email: str, firebase_uid: str) -> Tuple[str, str]:
        """Gera um par de tokens (access e refresh)"""
        
        access_token = self._gerar_acess_token(email, firebase_uid)
        refresh_token = self._gerar_refresh_token(email, firebase_uid)
        
        
        self._auditar_token(
            user_id=firebase_uid,
            token_type="access",
            action="issue",
            token_jti=access_token['jti'] if 'jti' in access_token else None

        )
        self._auditar_token(
            user_id=firebase_uid,
            token_type="refresh",
            action="issue",
            token_jti=refresh_token['jti'] if 'jti' in refresh_token else None
        )
        
        return access_token, refresh_token
        
        
        # payload = {
        #     "email": email,
        #     "firebase_uid": firebase_uid,
        #     "exp": datetime.now(timezone.utc) + timedelta(hours=SecurityConfig.TOKEN_EXPIRE_HOURS)
        #     #"exp": datetime.utcnow() + timedelta(hours=SecurityConfig.TOKEN_EXPIRE_HOURS)
        # }
        # return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
        
        
        
        
        
    def refresh_tokens(self, refresh_token: str) -> Tuple[str, str]:
        """Gera novos access e refresh tokens a partir de um refresh token válido"""
        try:
            # 1. Verifica o refresh token
            payload = self.verificar_token(refresh_token, expected_type="refresh")
            
            # 2. Gera novos tokens
            new_access_token = self._gerar_access_token(payload["email"], payload["firebase_uid"])
            new_refresh_token = self._gerar_refresh_token(payload["email"], payload["firebase_uid"])
            
            # 3. Auditoria: invalida o token antigo
            self._audit_token(
                user_id=payload["firebase_uid"],
                token_type="refresh",
                action="invalidate",
                token_jti=payload.get("jti")
            )
            
            # 4. Auditoria: registra os novos tokens
            self._audit_token(
                user_id=payload["firebase_uid"],
                token_type="access",
                action="issue",
                token_jti=new_access_token.get("jti") if isinstance(new_access_token, dict) else None
            )
            
            self._audit_token(
                user_id=payload["firebase_uid"],
                token_type="refresh",
                action="issue",
                token_jti=new_refresh_token.get("jti") if isinstance(new_refresh_token, dict) else None
            )
            
            return new_access_token, new_refresh_token
            
        except Exception as e:
            self._audit_token(
                user_id=payload.get("firebase_uid") if 'payload' in locals() else None,
                token_type="refresh",
                action="verify_failed",
                error=str(e)
            )
        raise
        
        
        
        
    def _gerar_access_token(self, email: str, firebase_uid: str) -> str:
        """Gera um token JWT de acesso de curta duração"""
        payload = self.get_token_payload(email, firebase_uid)
        payload.update({
            "exp": datetime.now(timezone.utc) + timedelta(hours=SecurityConfig.TOKEN_EXPIRE_HOURS),
            "jti": str(uuid.uuid4()),  # Identificador único do token
            "type": "access"
        })
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
        
        
        
    def _gerar_refresh_token(self, email: str, firebase_uid: str) -> str:
        """Gera um token JWT de refresh de longa duração"""
        payload = self.get_token_payload(email, firebase_uid)
        payload.update({
            "exp": datetime.now(timezone.utc) + timedelta(days=SecurityConfig.REFRESH_TOKEN_EXPIRE_DAYS),
            "jti": str(uuid.uuid4()),  # Identificador único do token
            "type": "refresh"
        })
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
    
    
    
    def verificar_token(self, token: str, expected_type: Optional[str] = None) -> dict:
        """Valida o token e retorna o payload"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            # return jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            
            if expected_type and payload.get != expected_type:
                raise ValueError(f"Tipo de token inválido. Esperado: {expected_type}")
            
            
            self._auditar_token(
                user_id=payload.get("firebase_uid"),
                token_type=payload.get("type"),
                action="verify",
                token_jti=payload.get("jti")
            )
            
            return payload
        except (jwt.ExpiredSignatureError, jwt.InvalidTokenError) as e:
            # Registrar falha na verificação
            try:
                invalid_payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm], options={"verify_exp": False})
                self._auditar_token(
                    user_id=invalid_payload.get("firebase_uid"),
                    token_type=invalid_payload.get("type"),
                    action="verify_failed",
                    token_jti=invalid_payload.get("jti"),
                    error=str(e)
                )
            except:
                pass
            
            raise ValueError(f"Token inválido: {str(e)}")
                
        
        # except (jwt.ExpiredSignatureError, jwt.InvalidTokenError) as e:
        #     raise ValueError(f"Token inválido: {str(e)}")
        
        
        
        
    def refresh_access_token(self, refresh_token: str) -> Tuple[str, str]:
        """Gera um novo access token a partir de um refresh token válido"""
        # Verificar se é um refresh token válido
        
        payload = self.verificar_token(refresh_token, expected_type="refresh")
        
        
        new_access_token = self._gerar_access_token(payload["email"], payload["firebase_uid"])
        new_refresh_token = self._gerar_refresh_token(payload["email"], payload["firebase_uid"])
        
        
        
        # Invalidar o refresh token antigo
        self._audit_token(
            user_id=payload["firebase_uid"],
            token_type="refresh",
            action="invalidate",
            token_jti=payload.get("jti")
        )
        
        
        # Registrar emissão dos novos tokens
        self._audit_token(
            user_id=payload["firebase_uid"],
            token_type="access",
            action="issue",
            token_jti=new_access_token['jti'] if 'jti' in new_access_token else None
        )
        self._auditar_token(
            user_id=payload["firebase_uid"],
            token_type="refresh",
            action="issue",
            token_jti=new_refresh_token['jti'] if 'jti' in new_refresh_token else None
        )
        
        
        
        return new_access_token, new_refresh_token

    
    
    
    def _auditar_token(self, user_id: str, token_type: str, action: str, token_jti: str = None, error: str = None):
        """Registra ações relacionadas a tokens para auditoria"""
        
        audit_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "user_id": user_id,
            "token_type": token_type,
            "action": action,
            "token_jti": token_jti,
            "error": error
        }
        
        
        self.token_audit_log.append(audit_entry)
        print(f"[AUDIT] {audit_entry}")
        
        
        
    def get_audit_log(self, user_id: str = None):
        """Retorna registros de auditoria (opcionalmente filtrados por usuário)"""
        if user_id:
            return [entry for entry in self.token_audit_log if entry.get("user_id") == user_id]
        return self.token_audit_log
        
        

    def get_token_payload(self, email: str, firebase_uid: str) -> dict:
        """Retorna os dados básicos necessários para o payload do token"""
        if not email or not firebase_uid:
            raise ValueError("Email e firebase_uid são obrigatórios para gerar o token")
        return {
            "email": email,
            "firebase_uid": firebase_uid
        }
        
        
        
    def gerar_token(self, email: str, firebase_uid: str) -> str:
        """Método legado - mantido para compatibilidade"""
        return self._gerar_access_token(email, firebase_uid)
        
        
        
    def obter_identidade_usuario(self, token: str) -> dict:
        """Obtém a identidade do usuário a partir do token"""
        payload = self.verificar_token(token, expected_type="access")
        return {
            "email": payload["email"],
            "firebase_uid": payload["firebase_uid"]
    }