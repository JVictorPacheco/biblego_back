import jwt
from datetime import datetime, timedelta
from app.Models.usuario import Usuario
from app.Service.token_service import TokenService
from app.Repository.usuario_repository import UsuarioRepository
from werkzeug.exceptions import Unauthorized
import bcrypt
from flask import current_app, request



class AuthService:
    def __init__(self):
        self.token_service = TokenService()
        self.usuario_repo = UsuarioRepository()


    def login(self, email, senha):
        
        """Autentica usuário e retorna tokens"""
        try:
            usuario = self.validar_credenciais(email, senha)
            
            # Gera par de tokens (access + refresh)
            tokens = self.token_service.gerar_par_tokens(usuario['email'], usuario['firebase_uid'])
            
            # Decodifica o access token para obter o jti (para auditoria)
            try:
                decoded = jwt.decode(
                    tokens['access_token'], 
                    self.token_service.secret_key, 
                    algorithms=[self.token_service.algorithm]
                )
                
                # Auditoria de login (SUCESSO) - já é feita no gerar_tokens, mas podemos manter para login específico
                self.token_service._audit_token(
                    user_id=usuario['firebase_uid'],
                    token_type='login',
                    action='login_success',
                    token_jti=decoded['jti'],
                    ip_address=request.remote_addr if hasattr(request, 'remote_addr') else None,
                    user_agent=request.headers.get('User-Agent') if hasattr(request, 'headers') else None
                )
            except Exception as e:
                current_app.logger.error(f"Falha ao auditar token de login: {str(e)}")
            
            return {
                "access_token": tokens['access_token'],
                "refresh_token": tokens['refresh_token'],
                "token_type": tokens['token_type'],
                "expires_in": tokens['expires_in'],
                "mensagem": "Login realizado com sucesso",
                "usuario": {
                    "id": usuario["id"],
                    "email": usuario["email"],
                    "nome": usuario.get("nome"),
                    "firebase_uid": usuario["firebase_uid"]
                }
            }
            
        except Exception as e:
            # Auditoria de login (FALHA)
            self.token_service._audit_token(
                user_id=email,  # Usa email como identificador quando não tem firebase_uid
                token_type='login',
                action='login_failed',
                error=str(e),
                ip_address=request.remote_addr if hasattr(request, 'remote_addr') else None,
                user_agent=request.headers.get('User-Agent') if hasattr(request, 'headers') else None
            )
            raise




    def _validar_senha(self, senha: str, senha_hash: str) -> bool:
        return bcrypt.checkpw(senha.encode('utf-8'), senha_hash.encode('utf-8'))




    def obter_usuario_por_token(self, token: str) -> dict:
        """Obtém usuário completo a partir do token JWT"""
        payload = self.token_service.obter_identidade_usuario(token)
        usuario = self.usuario_repo.buscar_usuario_por_firebase_uid(payload["firebase_uid"])
        if not usuario:
            raise Unauthorized("Usuário não encontrado")
        return usuario        
            


    def validar_credenciais(self, email, senha):
        """Valida as credenciais do usuário e retorna os dados se válido"""
        try:
            # Busca o usuário pelo email usando seu repository
            usuario = self.usuario_repo.buscar_usuario_por_email(email)
            
            if not usuario:
                raise Unauthorized("Usuário não encontrado")
            
            # Verifica a senha usando seu método existente
            # O campo no dicionário retornado é 'senha_hash' (conforme o zip no repository)
            if not self._validar_senha(senha, usuario['senha_hash']):
                raise Unauthorized("Senha incorreta")
            
            # Retorna os dados do usuário no formato esperado
            return {
                "id": usuario["id"],
                "email": usuario["email"], 
                "nome": usuario.get("nome"),
                "firebase_uid": usuario["firebase_uid"]
            }
            
        except Unauthorized:
            # Re-levanta erros de autorização
            raise
        except Exception as e:
            current_app.logger.error(f"Erro na validação de credenciais: {str(e)}")
            raise Unauthorized("Erro na autenticação")

