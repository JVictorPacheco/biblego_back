from app.Repository.usuario_repository import UsuarioRepository
from app.Models.usuario import Usuario
from werkzeug.security import generate_password_hash


class UserService:
    def __init__ (self):
        self.user_repository = UsuarioRepository()
        # self.task_repository = task_repository

    def criar_usuario(self, usuario_data):

            # Validar campos antes de chamar repository
            campos_obrigatorios = ['nome', 'email', 'telefone', 'cidade', 
                                'estado', 'endereco', 'sexo', 
                                'data_nascimento', 'firebase_uid', 'senha']
            
            
            for campo in campos_obrigatorios:
                if not usuario_data.get(campo):
                    raise ValueError(f"Campo obrigatório faltando: {campo}")
            
            
            # for campo in campos_obrigatorios:
            #     if campo not in usuario_data:
            #         raise ValueError(f"Campo obrigatório faltando: {campo}")

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
       #  'email': lambda x: re.match(r"[^@]+@[^@]+\.[^@]+", x),
       #  'status_conta_usuario': lambda x: x.lower() in ['ativo', 'inativo', 'pendente']
        
    }
    
    def atualizar_usuario(self, user_id, novos_dados):
        
        """
        Valida e atualiza os dados do usuário
        :param user_id: ID do usuário (obtido do token JWT)
        :param novos_dados: Dicionário com campos para atualização
        :return: Tuple (dict, int) - (resposta, status_code)
        """
        # 1. Validação do ID (agora vindo do token)
        if not isinstance(user_id, int) or user_id <= 0:
            return {"Erro": "ID de usuário inválido"}, 400

        # 2. Filtra campos permitidos
        dados_validados = {
            campo: valor
            for campo, valor in novos_dados.items()
            if campo in UserService.CAMPOS_PERMITIDOS
        }

        # 3. Verifica se há campos válidos para atualização
        if not dados_validados:
            return {"Erro": "Nenhum campo permitido para atualização"}, 400

        # 4. Validações específicas por campo
        for campo, valor in dados_validados.items():
            # 4.1 Valida campos com regras especiais
            if campo in UserService.REGRAS_ESPECIAIS:
                if not UserService._validar_campo(campo, valor):
                    return {"Erro": f"Valor inválido para o campo {campo}"}, 400
            
            # 4.2 Tratamento especial para senha (se necessário)
            if campo == 'senha':
                dados_validados[campo] = generate_password_hash(valor)  # Descomente se usar
                
            # 4.3 Formatação de campos específicos
            if campo == 'status_conta_usuario' and isinstance(valor, str):
                dados_validados[campo] = valor.capitalize()

        # 5. Bloqueia campos sensíveis (proteção adicional)
        campos_protegidos = ['id', 'firebase_uid', 'data_criacao']
        if any(campo in dados_validados for campo in campos_protegidos):
            return {"Erro": "Campos protegidos não podem ser alterados"}, 403

        # 6. Executa a atualização no repositório
        try:
            return UsuarioRepository().atualizar_usuario(user_id, dados_validados)
        except Exception as e:
            return {"erro": f"Falha ao atualizar usuário: {str(e)}"}, 500
    
    
    
    
    def deletar_usuario(user_id):
        """
        Valida e deleta um usuário
        :param user_id: ID do usuário (int)
        :return: Tuple (dict, int) - (mensagem, status_code)
        """
        # Validação básica do ID
        if not isinstance(user_id, int) or user_id <= 0:
            return {"Erro": "ID inválido"}, 400

        try:
            # Verifica se o usuário existe
            if not UsuarioRepository.usuario_existe(user_id):
                return {"Erro": "Usuário não encontrado"}, 404

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


