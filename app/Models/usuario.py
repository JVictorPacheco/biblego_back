#Inicializa os parâmetros de conexão
import bcrypt
from werkzeug.security import check_password_hash


class Usuario:

    __tablename__ = "usuarios"
    
    class Usuario:
    
     def __init__(self, id=None, email=None, senha=None, **kwargs):
        self.id = id    # Pode ser None para novos usuários
        self.email = email
        self.senha = senha
        
        # Campos opcionais com valores padrão
        self.nome = kwargs.get('nome')
        self.telefone = kwargs.get('telefone')
        self.cidade = kwargs.get('cidade')
        self.estado = kwargs.get('estado')
        self.endereco = kwargs.get('endereco')
        self.is_premium = kwargs.get('is_premium', False)
        self.data_assinatura_premium = kwargs.get('data_assinatura_premium')
        self.plano_premium = kwargs.get('plano_premium')
        self.data_final_premium = kwargs.get('data_final_premium')
        self.idade = kwargs.get('idade')
        self.sexo = kwargs.get('sexo')
        self.data_nascimento = kwargs.get('data_nascimento')
        self.status_conta = kwargs.get('status_conta_usuario', True)
        self.notificacao_habilitada = kwargs.get('notificacao_habilitada', True)
        self.termos_aceitos = kwargs.get('termos_aceitos', True)
        self.cod_verificacao = kwargs.get('cod_verificacao')
        self.url_foto = kwargs.get('url_foto')

    def verificar_senha(self, senha_fornecida):
        if not hasattr(self, 'senha') or not isinstance(self.senha, str) or not self.senha.startswith("$2b$"):
            raise ValueError("Hash de senha inválido no banco de dados")
        return bcrypt.checkpw(
            senha_fornecida.encode('utf-8'),
            self.senha.encode('utf-8')
        )
