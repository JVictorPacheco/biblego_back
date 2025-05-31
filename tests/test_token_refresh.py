"""
Teste unitario do token refresh
"""
import pytest
from app.Service.token_service import TokenService
from app.Service.auth_service import AuthService
from app.Repository.token_audit_repository import TokenAuditRepository
from app.Models.token_audit import AuditAction, TokenType




@pytest.fixture
def token_service():
    return TokenService()

@pytest.fixture
def auth_service():
    return AuthService()


def test_token_refresh_flow(auth_service, token_service):
        """Teste completo do fluxo de refresh token"""
        # 1. Simula login (em produção, use credenciais reais)
        user_id = "test_user_123"
        email = "test@example.com"
        
        # Gera tokens iniciais (usando o nome correto do método)
        access_token, refresh_token = token_service._gerar_access_token(email, user_id)
        
        # 2. Verifica se os tokens foram auditados
        audit_repo = TokenAuditRepository()
        audits = audit_repo.get_by_user(user_id)
        
        assert any(a.action == AuditAction.ISSUE and a.token_type == TokenType.ACCESS for a in audits)
        assert any(a.action == AuditAction.ISSUE and a.token_type == TokenType.REFRESH for a in audits)
        
        # 3. Usa o refresh token para obter novos tokens
        # ATENÇÃO: Aqui você precisa usar o nome do método que faz refresh no seu serviço
        # Se for 'renovar_token' ou outro nome, ajuste aqui
        new_access, new_refresh = token_service._gerar_refresh_token(refresh_token)
        
        # 4. Verifica se gerou novos tokens diferentes
        assert new_access != access_token
        assert new_refresh != refresh_token
        
        # 5. Verifica auditoria do refresh
        audits_after_refresh = audit_repo.get_by_user(user_id)
        
        assert any(
            a.action == AuditAction.INVALIDATE and 
            a.token_type == TokenType.REFRESH and
            a.token_jti in refresh_token
            for a in audits_after_refresh
        )
        
        assert any(a.action == AuditAction.ISSUE and a.token_type == TokenType.ACCESS for a in audits_after_refresh)
        assert any(a.action == AuditAction.ISSUE and a.token_type == TokenType.REFRESH for a in audits_after_refresh)

def test_invalid_refresh_token(token_service):
        """Teste com refresh token inválido"""
        invalid_token = "token_invalido.123.456"
        
        with pytest.raises(ValueError):
            # Ajuste para o nome do método correto no seu serviço
            token_service._gerar_refresh_token(invalid_token)
        
        audits = TokenAuditRepository().get_by_user(None, limit=10)
        assert any(
            a.action == AuditAction.VERIFY_FAILED and 
            "Token inválido" in (a.error or "")
            for a in audits
        )