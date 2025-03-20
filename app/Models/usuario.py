#Inicializa os parâmetros de conexão
class Usuario:

    __tablename__ = "usuarios"
        
    def __init__(self, id, name, email, telefone, cidade, 
                 estado, endereco, is_premium, data_assinatura_premium, 
                 plano_premium, data_final_premium, idade, sexo, data_nascimento, 
                 status_conta, notificacao_habilitada, termos_aceitos, cod_verificacao, url_foto, senha ):
        
        self.id = id
        self.name = name
        self.email = email
        self.telefone = telefone
        self.cidade = cidade
        self.estado = estado
        self.endereco = endereco
        self.is_premium = is_premium
        self.data_assinatura_premium = data_assinatura_premium
        self.plano_premium = plano_premium
        self.data_final_premium = data_final_premium
        self.idade = idade
        self.sexo = sexo
        self.data_nascimento = data_nascimento
        self.status_conta = status_conta
        self.notificacao_habilitada = notificacao_habilitada
        self.termos_aceitos = termos_aceitos
        self.cod_verificacao = cod_verificacao
        self.url_foto = url_foto
        self.senha = senha


    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'telefone': self.telefone,
            'cidade': self.cidade,
            'estado': self.estado,
            'endereco': self.endereco,
            'email': self.email,
            'is_premium': self.is_premium,
            'data_assinatura_premium': self.data_assinatura_premium,
            'plano_premium': self.plano_premium,
            'data_final_premium': self.data_final_premium,
            'idade': self.idade,
            'sexo': self.sexo,
            'email': self.email,
            'data_nascimento': self.data_nascimento,
            'status_conta': self.status_conta,
            'notificacao_habilitada': self.notificacao_habilitada,
            'termos_aceitos': self.termos_aceitos,
            'cod_verificacao': self.cod_verificacao,
            'url_foto': self.url_foto,
            'senha': self.senha
        }
