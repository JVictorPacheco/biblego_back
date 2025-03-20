import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import unittest
from unittest.mock import MagicMock, patch
from app.Repository.usuario_repository import UsuarioRepository


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
        # Chama o método sob teste
        resultado = UsuarioRepository.criar_usuario(self, self.usuario)
        
        # Verifica se o execute foi chamado
        self.mock_cursor.execute.assert_called()
        
        # Verifica se o commit foi chamado
        self.mock_connection.commit.assert_called()
        
        # Verifica o retorno esperado
        self.assertIsNone(resultado)
    
    def test_criar_usuario_falha(self):
        """Testa o tratamento de erro na criação de usuário"""
        # Configura o execute para lançar exceção
        self.mock_cursor.execute.side_effect = Exception("Erro ao executar a query")
        
        # Chama o método sob teste
        resultado = UsuarioRepository.criar_usuario(self, self.usuario)
        
        # Verifica se rollback foi chamado
        self.mock_connection.rollback.assert_called()
        
        # Verifica o retorno esperado
        self.assertEqual(resultado[0], {"erro": "Erro ao executar a query"})
        self.assertEqual(resultado[1], 500)

if __name__ == "__main__":
    unittest.main()