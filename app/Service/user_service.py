from app.Repository.usuario_repository import UsuarioRepository


class UserService:
    def __init__ (self):
        self.user_repository = UsuarioRepository()
        # self.task_repository = task_repository

    def user_create(self, usuario_data):
        return self.user_repository.criar_usuario(usuario_data)
    
    



