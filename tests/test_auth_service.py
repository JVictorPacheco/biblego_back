import pytest
from unittest.mock import MagicMock, patch
from app.Service.auth_service import AuthService
from werkzeug.exceptions import Unauthorized
import bcrypt


@pytest.fixture
def mock_repo():
    return MagicMock()


@pytest.fixture
def auth_service(mock_repo):
    service = AuthService()
    service.usuario_repo = mock_repo
    return service


# ---- Testes para login() ----
def test_login_sucesso(auth_service, mock_repo):
    """Testa login com credenciais válidas"""
    # Configura mock
    mock_repo.buscar_usuario_por_email.return_value = {
        'email': 'teste@email.com',
        'senha_hash': bcrypt.hashpw('senha123'.encode(), bcrypt.gensalt()).decode(),
        'firebase_uid': 'uid123',
        'id': 1,
        'nome': 'Teste'
    }
    
    #executa
    result = auth_service.login('teste@email.com', 'senha123')



    assert 'token' in result
    assert result['usuario']['email'] == 'teste@email.com'
    
    
    
def test_login_credenciais_invalidas(auth_service, mock_repo):
    """Testa login com senha incorreta"""
    mock_repo.buscar_usuario_por_email.return_value = {
        'email': 'teste@email.com',
        'senha_hash': bcrypt.hashpw('senha123'.encode(), bcrypt.gensalt()).decode()
    }

    with pytest.raises(Unauthorized):
        auth_service.login('teste@email.com', 'senha_errada')



def test_validar_credenciais_usuario_nao_existe(auth_service, mock_repo):
    """Testa quando usuário não existe"""
    mock_repo.buscar_usuario_por_email.return_value = None

    with pytest.raises(Unauthorized):
        auth_service.validar_credenciais('inexistente@email.com', 'qualquer')



def test_validar_senha_correta(auth_service):
    """Testa validação de senha correta"""
    senha = 'senha123'
    senha_hash = bcrypt.hashpw(senha.encode(), bcrypt.gensalt()).decode()
    
    assert auth_service._validar_senha(senha, senha_hash) is True
    
    
    
def test_validar_senha_incorreta(auth_service):
    """Testa validação de senha incorreta"""
    senha_hash = bcrypt.hashpw('senha123'.encode(), bcrypt.gensalt()).decode()
    
    assert auth_service._validar_senha('outrasenha', senha_hash) is False
    
    
    
    
# def test_login_email_invalido(auth_service, mock_repo):
#     """Testa login com email mal formatado"""
#     mock_repo.buscar_usuario_por_email.return_value = {
#         'email': 'teste@email.com',
#         'senha_hash': bcrypt.hashpw('senha123'.encode(), bcrypt.gensalt()).decode()
#     }


#     with pytest.raises(Unauthorized):
#         auth_service.login('inexistente@email.com', 'senha123')