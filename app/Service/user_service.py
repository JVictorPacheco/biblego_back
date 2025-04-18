from app.Repository.usuario_repository import UsuarioRepository
from app.Models.usuario import Usuario
# from werkzeug.security import generate_password_hash


class UserService:
    def __init__ (self):
        self.user_repository = UsuarioRepository()
        # self.task_repository = task_repository

    def criar_usuario(self, usuario_data):

            # Validação básica
        campos_obrigatorios = ['nome', 'email', 'telefone', 'cidade', 
                              'estado', 'endereco', 'sexo', 
                              'data_nascimento', 'firebase_uid']
        
        for campo in campos_obrigatorios:
            if campo not in usuario_data:
                raise ValueError(f"Campo obrigatório faltando: {campo}")

        usuario = Usuario(**usuario_data)
        return self.user_repository.criar_usuario(usuario)
            
    
    
    # Usados para o def atualizar_usuario
    CAMPOS_PERMITIDOS = {
        'nome', 'telefone', 'cidade', 'estado', 'endereco', 'is_premium',
        'data_assinatura_premium', 'plano_premium', 'data_final_premium', 'idade',
        'sexo', 'data_nascimento', 'status_conta_usuario', 'notificacao_habilitada', 
        'termos_aceitos', 'cod_verificacao', 'url_foto'
    }
    
    REGRAS_ESPECIAIS = {
        'senha': lambda v: len(v) >= 8  # Validação personalizada
    }
    
    def atualizar_usuario(user_id, novos_dados):
        if not isinstance(user_id, int) or user_id <= 0:
            return {"Erro": "ID Inválido"}, 400
        
        dados_validados = {
            campo: valor
        for campo, valor in novos_dados.items()
                if campo in UserService.CAMPOS_PERMITIDOS
        }  
        
        
        for campo, valor in dados_validados.items():
         if campo in UserService.REGRAS_ESPECIAIS:
            if not UserService._validar_campo(campo, valor):
                return {"Erro": f"Valor inválido para {campo}"}, 400
        
        # if campo == 'senha':
        #     valor = generate_password_hash(valor)
        
        if campo == 'status_conta_usuario' and isinstance(valor, str):
            dados_validados[campo] = valor.capitalize()
            
            
        if not dados_validados:
         return {"Erro": "Nenhum campo válido para atualização"}, 400
        
        
        try: 
            return UsuarioRepository().atualizar_usuario(user_id, dados_validados)
        except Exception as e:
            return {"erro": str(e)}, 500
    
    
    
    
    def deletar_usuario(user_id):
        """
        Valida e deleta um usuário
        :param user_id: ID do usuário (obtido do token JWT)
        :return: Tuple (dict, int) - (mensagem, status_code)
        """
        # Validação básica do ID
        if not isinstance(user_id, int) or user_id <= 0:
            return {"Erro": "ID inválido"}, 400

        try:
            
            # Deleção efetiva
            return UsuarioRepository.deletar_usuario(user_id)
            
        except Exception as e:
            return {"erro": f"Falha ao deletar usuário: {str(e)}"}, 500
    
    


    def obter_usuario_por_id(self, user_id):
        # Adicione este método no UserService
        """Obtém um usuário pelo ID"""
        # Implementação depende do seu repositório
        # Exemplo básico:
        return self.user_repository.buscar_usuario_por_id(user_id)
    
    
    
    
    def obter_usuario_por_email(self, email: str) -> dict:
       print(f"[DEBUG] Buscando usuário por email: {email}")
       usuario = self.user_repository.buscar_usuario_por_email(email)
       print(f"[DEBUG] Resultado da busca: {usuario}")
       if not usuario:
            raise ValueError("Usuário não encontrado")
        
       usuario.pop('senha_hash', None)
       return usuario
   
   
   
   
    def deletar_usuario(user_id):
        """
        Valida e deleta um usuário
        :param user_id: ID do usuário (obtido do token JWT)
        :return: Tuple (dict, int) - (mensagem, status_code)
        """
        # Validação básica do ID
        if not isinstance(user_id, int) or user_id <= 0:
            return {"Erro": "ID inválido"}, 400

        try:
            # Deleção efetiva
            return UsuarioRepository.deletar_usuario(user_id)
            
        except Exception as e:
            return {"erro": f"Falha ao deletar usuário: {str(e)}"}, 500


