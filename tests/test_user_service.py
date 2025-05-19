import unittest
from unittest.mock import patch, MagicMock
from app.Service.user_service import UserService

class TestUserService(unittest.TestCase):
    def setUp(self):
        self.service = UserService()
        self.campos_obrigatorios = [
            'nome', 'email', 'telefone', 'cidade',
            'estado', 'endereco', 'sexo',
            'data_nascimento', 'firebase_uid', 'senha'
        ]
        self.dados_validos = {
            'nome': 'Teste',
            'email': 'teste@email.com',
            'telefone': '11999999999',
            'cidade': 'São Paulo',
            'estado': 'SP',
            'endereco': 'Rua Teste',
            'sexo': 'M',
            'data_nascimento': '2000-01-01',
            'firebase_uid': 'abc123',
            'senha': 'senha123'
        }
        
        
        
        
      
    def test_criacao_usuario_valido(self):
        """Teste de fluxo positivo"""
        with patch('app.Service.user_service.UsuarioRepository') as mock_repo:
            mock_repo.return_value.criar_usuario.return_value = 123
            service = UserService()
        
        result = service.criar_usuario(self.dados_validos)
        
        self.assertEqual(result, 123)
        mock_repo.return_value.criar_usuario.assert_called_once()


    # @patch('app.Service.user_service.UsuarioRepository') 
    # def test_campos_obrigatorios(self, mock_repo):
    #     """Testa validação de campos obrigatórios"""
    #     # Configuração do mock
    #     mock_repo = MagicMock()
    #     self.service.user_repository = mock_repo
        
    #     for campo in self.campos_obrigatorios:
    #         with self.subTest(campo=campo):
    #             dados = self.dados_validos.copy()
    #             dados[campo] = None  # Remove o campo sendo testado
            
    #         # Testa se o ValueError é lançado
    #         with self.assertRaises(ValueError) as context:
    #             self.service.criar_usuario(dados)
            
    #         # Verificações adicionais
    #         self.assertIn(f"Campo obrigatório faltando: {campo}", str(context.exception))
    #         mock_repo.criar_usuario.assert_not_called()




if __name__ == '__main__':
    unittest.main()