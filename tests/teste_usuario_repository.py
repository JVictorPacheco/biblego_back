import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import unittest
from unittest.mock import MagicMock, patch
from app.Repository.usuario_repository import UsuarioRepository
from app.Service.user_service import UserService


class MockUsuario:
    """Mock para simular um usuário com atributos fictícios"""
    def __init__(self):
        self.nome = "João Silva"
        self.email = "joao@email.com"
        self.telefone = "123456789"
        self.cidade = "Rio de Janeiro"
        self.estado = "RJ"
        self.endereco = "Rua 123"
        self.is_premium = False
        self.data_assinatura_premium = None
        self.plano_premium = None
        self.data_final_premium = None
        self.idade = 25
        self.sexo = "M"
        self.data_nascimento = "1999-01-01"
        self.status_conta = "Ativo"
        self.notificacao_habilitada = True
        self.termos_aceitos = True
        self.cod_verificacao = "ABC123"
        self.url_foto = "http://example.com/foto.jpg"
        self.senha = "senha123"
        self.firebase_uid = "mock_firebase_uid123"
        
        

class TestUsuarioRepository(unittest.TestCase):
    def setUp(self):
        # Cria o mock para o banco de dados
        self.patcher = patch('app.Repository.usuario_repository.get_db_connection')
        self.mock_get_db = self.patcher.start()
        
        # Configura o mock para a conexão
        self.mock_db = MagicMock()
        self.mock_cursor = MagicMock()
        self.mock_connection = MagicMock()
        
        # Configura a estrutura de objetos mock
        self.mock_db.cursor = self.mock_cursor
        self.mock_db.connection = self.mock_connection
        
        # Define o retorno da função get_db_connection
        self.mock_get_db.return_value = self.mock_db
        
        # Cria o objeto usuário mock
        self.usuario = MockUsuario()
    
    def tearDown(self):
        self.patcher.stop()
    
    def test_criar_usuario_sucesso(self):
        """Testa a criação de usuário com sucesso"""
        
        
        self.mock_cursor.fetchone.return_value = [123]
        
        self.usuario.firebase_uid = "test_uid"
        
        with patch('bcrypt.hashpw') as mock_hash:
            mock_hash.return_value = b'hashed_password'
            
            # Execução
            resultado = UsuarioRepository.criar_usuario(self, self.usuario)
            
            # Verificações
            self.mock_cursor.execute.assert_called_once()
            self.mock_connection.commit.assert_called_once()
            self.assertEqual(resultado, 123)
        
        
        
        
        
    
    def test_criar_usuario_falha_no_banco(self):
        """Testa falha no banco de dados durante criação"""
        # Configura
        self.mock_cursor.execute.side_effect = Exception("Erro de conexão com o banco")
        
        # Executa + Verifica
        with self.assertRaises(Exception) as context:
            UsuarioRepository.criar_usuario(self, self.usuario)
        
        # Asserts
        self.assertEqual(str(context.exception), "Erro de conexão com o banco")
        self.mock_connection.rollback.assert_called_once()  # Verifica rollback
            

            
        
        

if __name__ == "__main__":
    
    unittest.main()