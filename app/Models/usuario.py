#Inicializa os parâmetros de conexão
import bcrypt
from werkzeug.security import check_password_hash


class Usuario:

    __tablename__ = "usuarios"
    
    class Usuario:
    
     def __init__(self, id, email, senha, **kwargs):
        # Campos obrigatórios para autenticação
        self.id = id
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
        self.status_conta = kwargs.get('status_conta', True)
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
    
    
    
    
    
    
    
    
    
    
        
    # def __init__(self, id, nome, email, telefone, cidade, 
    #              estado, endereco, is_premium, data_assinatura_premium, 
    #              plano_premium, data_final_premium, idade, sexo, data_nascimento, 
    #              status_conta, notificacao_habilitada, termos_aceitos, cod_verificacao, url_foto, senha ):
        
    #     self.id = id
    #     self.nome = nome
    #     self.email = email
    #     self.telefone = telefone
    #     self.cidade = cidade
    #     self.estado = estado
    #     self.endereco = endereco
    #     self.is_premium = is_premium
    #     self.data_assinatura_premium = data_assinatura_premium
    #     self.plano_premium = plano_premium
    #     self.data_final_premium = data_final_premium
    #     self.idade = idade
    #     self.sexo = sexo
    #     self.data_nascimento = data_nascimento
    #     self.status_conta = status_conta
    #     self.notificacao_habilitada = notificacao_habilitada
    #     self.termos_aceitos = termos_aceitos
    #     self.cod_verificacao = cod_verificacao
    #     self.url_foto = url_foto
    #     self.senha = senha


    # def to_dict(self):
    #     return {
    #         'id': self.id,
    #         'nome': self.nome,
    #         'email': self.email,
    #         'telefone': self.telefone,
    #         'cidade': self.cidade,
    #         'estado': self.estado,
    #         'endereco': self.endereco,
    #         'is_premium': self.is_premium,
    #         'data_assinatura_premium': self.data_assinatura_premium,
    #         'plano_premium': self.plano_premium,
    #         'data_final_premium': self.data_final_premium,
    #         'idade': self.idade,
    #         'sexo': self.sexo,
    #         'data_nascimento': self.data_nascimento,
    #         'status_conta': self.status_conta,
    #         'notificacao_habilitada': self.notificacao_habilitada,
    #         'termos_aceitos': self.termos_aceitos,
    #         'cod_verificacao': self.cod_verificacao,
    #         'url_foto': self.url_foto,
    #         'senha': self.senha
    #     }
    
    # def verificar_senha(self, senha_fornecida):
        
    #  if not hasattr(self, 'senha') or not isinstance(self.senha, str) or not self.senha.startswith("$2b$"):
    #     raise ValueError("Hash de senha inválido no banco de dados")
    #  return bcrypt.checkpw(
    #     senha_fornecida.encode('utf-8'),
    #     self.senha.encode('utf-8')
    # )