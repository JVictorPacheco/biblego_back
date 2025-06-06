import jwt
from datetime import datetime, timedelta, timezone
from app.Core.security_config import SecurityConfig
from datetime import datetime, timezone  # Adicione timezone
from typing import Tuple, Optional
import uuid
from typing import Optional, Dict, Any
from werkzeug.exceptions import Unauthorized
from app.Config.database import get_db_connection
from flask import request
from app.Repository.token_audit_repository import TokenAuditRepository
from app.Models.token_audit import TokenAuditCreate
import traceback



class TokenService:
    
    def __init__(self, audit_repository: TokenAuditRepository = None):
        self.secret_key = SecurityConfig.SECRET_KEY
        self.algorithm = SecurityConfig.ALGORITHM
        # Lembrar que em produção tenho que considerar injetar uma dependencia para auditoria
        self.audit_repository = audit_repository or TokenAuditRepository()
        print(f"[TOKEN SERVICE] Audit repo initialized: {hasattr(self, 'audit_repository')}")





    def _audit_token(self, user_id: str, token_type: str, action: str, **kwargs):
        """Método robusto de auditoria"""
        try:
            print(f"[AUDIT ATTEMPT] Action: {action} | User: {user_id}")
            
            audit_data = TokenAuditCreate(
                user_id=user_id,
                token_type=token_type,
                action=action,
                ip_address=request.remote_addr if hasattr(request, 'remote_addr') else None,
                user_agent=request.headers.get('User-Agent') if hasattr(request, 'headers') else None,
                **kwargs
            )
            
            result = self.audit_repository.create(audit_data)
            print(f"[AUDIT RESULT] {'Success' if result else 'Failed'}")
            
        except Exception as e:
            print(f"[AUDIT ERROR] {str(e)}")
            raise

    
    
    def gerar_tokens(self, email: str, firebase_uid: str) -> Tuple[str, str]:
        """Gera um par de tokens (access e refresh)"""
        
        access_token = self._gerar_access_token(email, firebase_uid)
        refresh_token = self._gerar_refresh_token(email, firebase_uid)
        
        
        print(f"[TOKEN] Verificando token. Algoritmo: {self.algorithm} | Key: {self.secret_key[:5]}...")
        
        
        self._audit_token(
            user_id=firebase_uid,
            token_type="access",
            action="issue",
            token_jti=access_token['jti'] if 'jti' in access_token else None

        )
        self._audit_token(
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
        """Renova access e refresh tokens"""
        try:
            token_service = TokenService()
        
        # Debug do token recebido
            print(f"[REFRESH INPUT] Token recebido: {refresh_token[:20]}...")
        
        # Verifica sem checar expiração primeiro
            try:
                payload = jwt.decode(
                    refresh_token,
                    token_service.secret_key,
                    algorithms=[token_service.algorithm],
                    options={"verify_exp": False}
                )
            except Exception as e:
                print(f"[DECODE ERROR] {str(e)}")
                raise ValueError("Token inválido")
            
                # Verificação manual da expiração
            if payload.get('exp'):
                    exp_time = datetime.fromtimestamp(payload['exp'], tz=timezone.utc)
                    current_time = datetime.now(timezone.utc)
                    print(f"[EXPIRATION CHECK] Expira: {exp_time} | Agora: {current_time}")
                    
            if current_time > exp_time:
                        # Token expirado mas pode ser aceito para refresh
                        print("[REFRESH WITH EXPIRED TOKEN] Permitindo renovação")
                        
                # Restante da lógica para gerar novos tokens...
            new_access = token_service._gerar_access_token(payload["email"], payload["firebase_uid"])
            new_refresh = token_service._gerar_refresh_token(payload["email"], payload["firebase_uid"])
                
            return {
                    "access_token": new_access,
                    "refresh_token": new_refresh
                }
        
        except Exception as e:
            print(f"[REFRESH SERVICE ERROR] {str(e)}")
            raise ValueError(str(e))
        
        
        
        
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
        try:
            # Adicione este debug para ver o token completo
            print(f"[DEBUG FULL TOKEN] {token}")
            
            payload = jwt.decode(
                token,
                self.secret_key,
                algorithms=[self.algorithm],
                options={"verify_exp": False}  # Primeiro decodifica sem verificar expiração
            )
            
            # Verificação manual da expiração
            if payload.get('exp') and datetime.now(timezone.utc) > datetime.fromtimestamp(payload['exp'], tz=timezone.utc):
                print(f"[TOKEN EXPIRADO] Expiração: {payload['exp']} | Now: {datetime.now(timezone.utc).timestamp()}")
                print(f"[TOKEN EXPIRED] Token expirado em {datetime.fromtimestamp(payload['exp'])}")
                raise jwt.ExpiredSignatureError("Token expirado")
            
            if expected_type and payload.get('type') != expected_type:
                raise ValueError("Tipo de token inválido")
                
            return payload
            
        except Exception as e:
            print(f"[VERIFY TOKEN ERROR] {str(e)}")
            raise
        except Exception as e:
            print(f"[TOKEN ERROR] {str(e)}")
            raise ValueError("Token inválido")
            
        
    def _auditar_token_falha(self, token: str, error_msg: str):
        """Método auxiliar para auditar falhas"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm], options={"verify_exp": False})
            self._audit_token(
                user_id=payload.get("firebase_uid"),
                token_type=payload.get("type"),
                action="verify_failed",
                token_jti=payload.get("jti"),
                error=error_msg
            )
        except:
            # Falha ao decodificar token para auditoria
            pass
        
        
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
        self._audit_token(
            user_id=payload["firebase_uid"],
            token_type="refresh",
            action="issue",
            token_jti=new_refresh_token['jti'] if 'jti' in new_refresh_token else None
        )
        
        
        
        return new_access_token, new_refresh_token

    
    
    
    def _audit_token(self, user_id: str, token_type: str, action: str, token_jti: str = None, error: str = None):
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