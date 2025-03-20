import sys
import os
import unittest
import uuid
from datetime import datetime

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app.Repository.usuario_repository import UsuarioRepository
from app.Config.database import get_db_connection

class Usuario:
    """Classe real de Usuário (você deve usar sua própria implementação)"""
    def __init__(self):
        self.nome = ""
        self.email = ""
        self.telefone = ""
        self.cidade = ""
        self.estado = ""
        self.endereco = ""
        self.is_premium = False
        self.data_assinatura_premium = None
        self.plano_premium = None
        self.data_final_premium = None
        self.idade = 0
        self.sexo = ""
        self.data_nascimento = ""
        self.status_conta = True
        self.notificacao_habilitada = True
        self.termos_aceitos = True
        self.cod_verificacao = ""
        self.url_foto = ""
        self.senha = ""

class TestIntegracaoUsuarioRepository(unittest.TestCase):
    def setUp(self):
        """Configura o ambiente para teste com banco real"""
        # Gera identificadores únicos para evitar conflitos
        self.id_unico = str(uuid.uuid4())[:8]
        
        # Cria um usuário de teste com identificadores únicos
        self.usuario = Usuario()
        self.usuario.nome = f"Teste {self.id_unico}"
        self.usuario.email = "teste@gmail.com" #f"teste_{self.id_unico}@exemplo.com"
        self.usuario.telefone = f"+5521{self.id_unico[:8]}"[:10]   
        self.usuario.cidade = "Cidade Teste"
        self.usuario.estado = "ST"
        self.usuario.endereco = "Rua de Teste, 123"
        self.usuario.is_premium = False
        self.usuario.data_assinatura_premium = None
        self.usuario.plano_premium = None
        self.usuario.data_final_premium = None
        self.usuario.idade = 30
        self.usuario.sexo = "Feminino"
        self.usuario.data_nascimento = "1995-05-05"
        self.usuario.status_conta = True
        self.usuario.notificacao_habilitada = True
        self.usuario.termos_aceitos = True
        self.usuario.cod_verificacao = "321667" #f"T{self.id_unico[:8]}"[:10]
        self.usuario.url_foto = f"http://teste.com/foto_{self.id_unico}.jpg"
        self.usuario.senha = f"senha_{self.id_unico}"
        
        # Instancia o repositório
        self.repo = UsuarioRepository()
        
        # Obtém conexão com o banco para uso nos testes e limpeza
        self.db = get_db_connection()
    
    def tearDown(self):
        """Limpa os dados de teste do banco"""
        # try:
        #     # Corrigindo: use o mesmo nome de tabela que no resto do código
        #     # e parâmetros de forma consistente
        #     sql = "DELETE FROM usuarios WHERE email = %(email)s"
        #     self.db.cursor.execute(sql, {"email": self.usuario.email})
        #     self.db.connection.commit()
        # except Exception as e:
        #     print(f"Erro ao limpar dados de teste: {e}")
        pass #     self.db.connection.rollback()
    
    def test_criar_usuario_integracao(self):
        """Testa a criação de usuário no banco real"""
        # Executa o método que queremos testar
        resultado = self.repo.criar_usuario(self.usuario)
        
        # Verifica se a operação foi bem-sucedida
        self.assertIsNone(resultado, "A criação do usuário deveria retornar None em caso de sucesso")
        
        # Opcional: Verifica se o usuário foi realmente inserido no banco
        sql = "SELECT nome, email FROM usuarios WHERE email = %(email)s"
        self.db.cursor.execute(sql, {"email": self.usuario.email})
        usuario_db = self.db.cursor.fetchone()
        
        self.assertIsNotNone(usuario_db, "O usuário deveria estar no banco de dados")
        self.assertEqual(usuario_db[0], self.usuario.nome, "O nome do usuário no banco deveria corresponder")

    def test_criar_usuario_falha_integracao(self):
        """Testa uma falha real na inserção (ex: violação de chave única)"""
        # Primeiro, cria o usuário
        self.repo.criar_usuario(self.usuario)
        
        # Tenta criar o mesmo usuário novamente (assumindo que email é chave única)
        resultado = self.repo.criar_usuario(self.usuario)
        
        # Verifica se retornou um erro como esperado
        self.assertIsNotNone(resultado, "Deveria retornar erro ao criar usuário duplicado")
        self.assertIsInstance(resultado, tuple, "O resultado de erro deveria ser uma tupla")
        self.assertEqual(resultado[1], 500, "O código de erro deveria ser 500")
        self.assertIn("erro", resultado[0], "A mensagem de erro deveria conter a chave 'erro'")

# Executar os testes se este arquivo for executado diretamente
if __name__ == "__main__":
    unittest.main()