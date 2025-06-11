from http.client import HTTPException
import jwt
from datetime import datetime, timedelta, timezone
from app.Core.security_config import SecurityConfig
from datetime import datetime, timezone  # Adicione timezone
from typing import Tuple, Optional
import uuid
from typing import Optional, Dict, Any
from flask import current_app, request
from app.Repository.token_audit_repository import TokenAuditRepository
from app.Models.token_audit import TokenAuditCreate




class TokenService:
    
    def __init__(self, audit_repository: TokenAuditRepository = None):
        self.secret_key = SecurityConfig.SECRET_KEY
        self.algorithm = SecurityConfig.ALGORITHM
        # Lembrar que em produção tenho que considerar injetar uma dependencia para auditoria
        self.audit_repository = audit_repository or TokenAuditRepository()
        current_app.logger.info(f"[TOKEN SERVICE INIT] Audit enabled: {SecurityConfig.TOKEN_AUDIT_ENABLED}")
        current_app.logger.info(f"[TOKEN SERVICE INIT] Audit repo methods: {dir(self.audit_repository)}")





    def _audit_token(self, user_id: str, token_type: str, action: str, **kwargs):
            """Versão robusta que não quebra o fluxo principal"""
            try:
                if not SecurityConfig.TOKEN_AUDIT_ENABLED:
                    return

                # Prepara dados adicionais garantindo tipos corretos
                audit_data = {
                    "user_id": str(user_id),  # Garante que é string
                    "token_type": str(token_type),  # Garante que é string
                    "action": str(action),  # Garante que é string
                    "ip_address": str(kwargs.get('ip_address')) if kwargs.get('ip_address') else None,
                    "user_agent": str(kwargs.get('user_agent')) if kwargs.get('user_agent') else None,
                    "error": str(kwargs.get('error')) if kwargs.get('error') else None,
                    "token_jti": str(kwargs.get('token_jti')) if kwargs.get('token_jti') else None
                }

                # Remove valores None
                audit_data = {k: v for k, v in audit_data.items() if v is not None}
                
                self.audit_repository.create(TokenAuditCreate(**audit_data))
                
            except Exception as e:
                current_app.logger.error(f"Falha na auditoria: {str(e)}", exc_info=True)
                            
        
        
        

    # def verificar_token(self, token: str, expected_type: Optional[str] = None) -> dict:
    #     try:
    #         # Decodifica sem verificar expiração inicialmente
    #         payload = jwt.decode(
    #             token,
    #             self.secret_key,
    #             algorithms=[self.algorithm],
    #             options={"verify_exp": False}
    #         )
            
    #         # Verificação manual da expiração
    #         if payload.get('exp') and datetime.now(timezone.utc) > datetime.fromtimestamp(payload['exp'], tz=timezone.utc):
    #             self._audit_token(
    #                 user_id=payload.get("firebase_uid"),
    #                 token_type=payload.get("type"),
    #                 action="token_expired",
    #                 token_jti=payload.get("jti"),
    #                 error="Token expirado"
    #             )
    #             raise jwt.ExpiredSignatureError("Token expirado")
                
    #         if expected_type and payload.get('type') != expected_type:
    #             error_msg = f"Tipo de token inválido. Esperado: {expected_type}, Recebido: {payload.get('type')}"
    #             self._audit_token(
    #                 user_id=payload.get("firebase_uid"),
    #                 token_type=payload.get("type"),
    #                 action="invalid_token_type",
    #                 token_jti=payload.get("jti"),
    #                 error=error_msg
    #             )
    #             raise ValueError(error_msg)
                
    #         return payload
            
    #     except Exception as e:
    #         current_app.logger.error(f"[VERIFY TOKEN ERROR] {str(e)}")
    #         raise

        
    
    def gerar_tokens(self, email, firebase_uid, token_type="access"):
        
        
        """Gera um token JWT (access ou refresh) com email e firebase_uid"""
        try:
            # Converte para string se necessário
            email = str(email) if email is not None else None
            firebase_uid = str(firebase_uid) if firebase_uid is not None else None
            
            # Validações
            if not email:
                raise ValueError("Email é obrigatório")
            if not firebase_uid:
                raise ValueError("Firebase UID é obrigatório")
            if token_type not in ["access", "refresh"]:
                raise ValueError("token_type deve ser 'access' ou 'refresh'")

            # Cria o payload
            payload = {
                "email": email,
                "firebase_uid": firebase_uid,
                "exp": datetime.now(timezone.utc) + (
                    timedelta(minutes=2) if token_type == "access" 
                    else timedelta(minutes=10)
                ),
                "jti": str(uuid.uuid4()),
                "type": token_type
            }
            
            # Gera o token
            token = jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
            
            # Auditoria
            self._audit_token(
                user_id=firebase_uid,
                token_type=token_type,
                action='issue',
                token_jti=payload['jti']
            )
            
            return token
            
        except Exception as e:
            # Auditoria de erro
            self._audit_token(
                user_id=firebase_uid if firebase_uid else 'unknown',
                token_type=token_type,
                action='issue_failed',
                error=str(e)
            )
            current_app.logger.error(f"Erro ao gerar token: {str(e)}")
            raise
        
        
        
        
    def gerar_par_tokens(self, email: str, firebase_uid: str) -> dict:
            """Gera um par completo de tokens (access + refresh) com email e firebase_uid"""
            try:
                access_token = self.gerar_tokens(email, firebase_uid, "access")
                refresh_token = self.gerar_tokens(email, firebase_uid, "refresh")
                
                return {
                    "access_token": access_token,
                    "refresh_token": refresh_token,
                    "token_type": "bearer",
                    "expires_in": 120  # 2 min
                }
                
            except Exception as e:
                self._audit_token(
                    user_id=firebase_uid,
                    token_type="pair",
                    action="generate_pair_failed",
                    error=str(e)
                )
                raise
                    
                
          
        
    def refresh_tokens(self, refresh_token: str) -> Tuple[str, str]:
            """Gera novos tokens a partir de um refresh token válido"""
            try:
                # Tenta verificar o token (incluindo tipo e expiração)
                try:
                    decoded = self.verificar_token(refresh_token, expected_type="refresh")
                    
                    # Se o refresh token ainda é válido, gera apenas novo access token
                    new_access_token = self.gerar_tokens(
                        decoded['email'], 
                        decoded['firebase_uid'], 
                        "access"
                    )
                    
                    self._audit_token(
                        user_id=decoded['firebase_uid'],
                        token_type='refresh',
                        action='refresh_success',
                        token_jti=decoded['jti']
                    )
                    
                    return {
                        "access_token": new_access_token,
                        "refresh_token": refresh_token  # Mantém o mesmo refresh token
                    }
                    
                except jwt.ExpiredSignatureError:
                    # Caso especial: refresh token expirado - gera novo par
                    decoded = jwt.decode(
                        refresh_token,
                        self.secret_key,
                        algorithms=[self.algorithm],
                        options={"verify_exp": False}
                    )
                    
                    # Verifica se o token expirado era realmente um refresh token
                    if decoded.get('type') != 'refresh':
                        self._audit_token(
                            user_id=decoded.get("firebase_uid", "unknown"),
                            token_type=decoded.get("type", "invalid"),
                            action="invalid_token_type",
                            token_jti=decoded.get("jti", ""),
                            error="Token expirado não é um refresh token"
                        )
                        raise ValueError("Token expirado não é um refresh token válido")
                    
                    # Gera novo par de tokens
                    new_access_token = self.gerar_tokens(
                        decoded['email'], 
                        decoded['firebase_uid'], 
                        "access"
                    )
                    new_refresh_token = self.gerar_tokens(
                        decoded['email'], 
                        decoded['firebase_uid'], 
                        "refresh"
                    )
                    
                    self._audit_token(
                        user_id=decoded.get("firebase_uid"),
                        token_type="refresh",
                        action="refresh_expired",
                        token_jti=decoded.get("jti"),
                        error="Refresh token expirado - gerado novo par"
                    )
                    
                    return {
                        "access_token": new_access_token,
                        "refresh_token": new_refresh_token
                    }
                    
            except ValueError as e:
                if "Tipo de token inválido" in str(e):
                    self._audit_token(
                        user_id='unknown',
                        token_type='invalid',
                        action='refresh_failed_wrong_type',
                        error=str(e)
                    )
                    from werkzeug.exceptions import HTTPException
                    raise HTTPException(response=400, description="Token fornecido não é um refresh token válido")
                raise
                
            except Exception as e:
                current_app.logger.error(f"Erro no refresh token: {str(e)}", exc_info=True)
                self._audit_token(
                    user_id='unknown',
                    token_type='refresh',
                    action='refresh_failed',
                    error=str(e)[:200]
                )
                from werkzeug.exceptions import HTTPException
                raise HTTPException(response=401, description="Falha ao renovar token")
                    
            
        
        
        
    # def _gerar_access_token(self, email: str, firebase_uid: str) -> str:
    #     """Gera um token JWT de acesso de curta duração"""
    #     payload = self.get_token_payload(email, firebase_uid)
    #     payload.update({
    #         "exp": datetime.now(timezone.utc) + timedelta(hours=SecurityConfig.TOKEN_EXPIRE_HOURS),
    #         "jti": str(uuid.uuid4()),  # Identificador único do token
    #         "type": "access"
    #     })
    #     return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
        
        
        
    # def _gerar_refresh_token(self, email: str, firebase_uid: str) -> str:
    #     """Gera um token JWT de refresh de longa duração"""
    #     payload = self.get_token_payload(email, firebase_uid)
    #     payload.update({
    #         "exp": datetime.now(timezone.utc) + timedelta(days=SecurityConfig.REFRESH_TOKEN_EXPIRE_DAYS),
    #         "jti": str(uuid.uuid4()),  # Identificador único do token
    #         "type": "refresh"
    #     })
    #     return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
    
    
    
    def verificar_token(self, token: str, expected_type: Optional[str] = None) -> dict:
        try:
            current_app.logger.debug(f"[DEBUG FULL TOKEN] {token}")
            
            payload = jwt.decode(
                token,
                self.secret_key,
                algorithms=[self.algorithm],
                options={"verify_exp": False}
            )
            
            # Validação da estrutura do payload
            if not isinstance(payload.get("firebase_uid"), str):
                raise ValueError("Campo firebase_uid inválido no token")
            if not isinstance(payload.get("type"), str):
                raise ValueError("Campo type inválido no token")

            self._audit_token(
                user_id=payload.get("firebase_uid"),
                token_type=payload.get("type"),
                action="verify",
                token_jti=payload.get("jti")
            )
            
            # Verificação de expiração
            if payload.get('exp') and datetime.now(timezone.utc) > datetime.fromtimestamp(payload['exp'], tz=timezone.utc):
                self._audit_token(
                    user_id=payload.get("firebase_uid"),
                    token_type=payload.get("type"),
                    action="verify_failed",
                    token_jti=payload.get("jti"),
                    error="Token expirado"
                )
                raise jwt.ExpiredSignatureError("Token expirado")
            
            # Verificação do tipo
            if expected_type and payload.get('type') != expected_type:
                error_msg = f"Tipo de token inválido. Esperado: {expected_type}, Recebido: {payload.get('type')}"
                self._audit_token(
                    user_id=payload.get("firebase_uid"),
                    token_type=payload.get("type"),
                    action="verify_failed",
                    token_jti=payload.get("jti"),
                    error=error_msg
                )
                raise ValueError(error_msg)
                
            return payload
            
        except Exception as e:
            current_app.logger.error(f"[VERIFY TOKEN ERROR] {str(e)}")
            self._auditar_token_falha(token, str(e))
            raise
            
        
    def _auditar_token_falha(self, token: str, error_msg: str):
       
        """Versão simplificada apenas para registrar erros"""
        try:
            # Tenta extrair informações do token sem validação
            payload = jwt.decode(token, options={"verify_signature": False})
            
            self._audit_token(
                user_id=payload.get("firebase_uid", "unknown"),
                token_type=payload.get("type", "invalid"),
                action="error",  # Novo tipo para erros
                token_jti=payload.get("jti", ""),
                error=error_msg[:200]  # Limita tamanho
            )
        except Exception:
            # Fallback mínimo se não conseguir decodificar
            self._audit_token(
                user_id="unknown",
                token_type="invalid",
                action="error",
                error=error_msg[:200]
            )
        
        
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

        

    def get_token_payload(self, email: str, firebase_uid: str) -> dict:
        """Retorna os dados básicos necessários para o payload do token"""
        if not email or not firebase_uid:
            raise ValueError("Email e firebase_uid são obrigatórios para gerar o token")
        return {
            "email": email,
            "firebase_uid": firebase_uid
        }
        
        
        
    # def gerar_token(self, email: str, firebase_uid: str) -> str:
    #     """Método legado - mantido para compatibilidade"""
    #     return self._gerar_access_token(email, firebase_uid)
          
            
        
        
        
    def obter_identidade_usuario(self, token: str) -> dict:
        """Obtém a identidade do usuário a partir do token"""
        payload = self.verificar_token(token, expected_type="access")
        return {
            "email": payload["email"],
            "firebase_uid": payload["firebase_uid"]
    }