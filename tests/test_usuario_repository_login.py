import pytest
from unittest.mock import MagicMock, patch
from app.Repository.usuario_repository import UsuarioRepository



@pytest.fixture
def mock_db():
    return MagicMock()




def buscar_usuario_por_email(mock_db):
    repo = UsuarioRepository()
    repo.get_db_connection = lambda: mock_db
    
    
    
    # Configura mock do banco
    mock_db.cursor.fetchone.return_value = (
        1, 'Nome', 'teste@email.com', None, None, None,
        False, None, None, None, 'uid123', 'hash_senha'
    )
    
    
    result = repo.buscar_usuario_por_email('teste@email.com')
    assert result['email'] == 'teste@email.com'
    assert result['firebase_uid'] == 'uid123' 
    assert result['senha'] == 'hash_senha'
    