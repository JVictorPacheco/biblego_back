from app.Repository.usuario_repository import UsuarioRepository


class TaskService:
    def __init__ (self):
        self.user_repository = UsuarioRepository()
        # self.task_repository = task_repository

    def get_all_tasks(self):
        return self.user_repository.criar_login_usuario()
    
    def add_task(self, title):
        if not title:
            raise ValueError("O título da tarefa não pode ser vazio")
        return self.user_repository.add_task(title)


