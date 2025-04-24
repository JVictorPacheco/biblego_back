import pytest
from datetime import datetime, timedelta
from app.Service.token_service import TokenService



@pytest.fixture
def token_service():
        return TokenService()
    
    


def teste_gerar_token(token_service):
    """Testa geração de token válido"""
    token = token_service.gerar_token('teste@email.com', 'uid123')
    assert isinstance(token, str)
    assert len(token.split('.')) == 3  # Header.Payload.Signature
    
    
    
    
    
def test_verificar_token_valido(token_service):
    token = token_service.gerar_token('teste@email.com', 'uid123')
    payload = token_service.verificar_token(token)
    
    
    assert payload['email'] == 'teste@email.com'
    assert payload['firebase_uid'] == 'uid123'
    assert 'exp' in payload
    
    
    
    
    
    
def test_verificar_token_invalido(token_service):
    with pytest.raises(ValueError):
        token_service.verificar_token('token.invalido.123')