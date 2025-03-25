from app.Repository.usuario_repository import UsuarioRepository
from app.Models.usuario import Usuario


class UserService:
    def __init__ (self):
        self.user_repository = UsuarioRepository()
        # self.task_repository = task_repository

    def user_create(self, usuario_data):

        usuario = Usuario(
            id=None,
            nome=usuario_data['nome'],
            email=usuario_data['email'],
            telefone=usuario_data['telefone'],
            cidade=usuario_data['cidade'],
            estado=usuario_data['estado'],
            endereco=usuario_data['endereco'],
            is_premium=False,
            data_assinatura_premium=None,
            plano_premium=None,
            data_final_premium=None,
            idade=None,
            sexo=usuario_data['sexo'],
            data_nascimento=usuario_data['data_nascimento'],
            status_conta=None,
            notificacao_habilitada=False,
            termos_aceitos=False,
            cod_verificacao=None,
            url_foto=None,
            senha=usuario_data['senha']
        )

        return self.user_repository.criar_usuario(usuario)
    
    



