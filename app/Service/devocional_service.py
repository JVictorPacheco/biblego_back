from typing import Optional, List, Dict, Any, Tuple
from datetime import datetime, date
from app.Repository.devocional_repository import DevocionalRepository
from app.Models.devocional import Devocional, DevocionalCreate, DevocionalUpdate
from werkzeug.exceptions import BadRequest, NotFound, Unauthorized
from flask import current_app


class DevocionalService:
    """
    Service responsável pela lógica de negócio dos devocionais.
    Aplica princípios SOLID e Clean Code para separar responsabilidades.
    """
    
    def __init__(self, devocional_repository: DevocionalRepository = None):
        """
        Inicializa o service com injeção de dependência.
        
        Args:
            devocional_repository: Repository para operações de dados (Dependency Injection)
        """
        self.devocional_repository = devocional_repository or DevocionalRepository()
        
        # Campos permitidos para atualização (Princípio da Responsabilidade Única)
        self.CAMPOS_PERMITIDOS_ATUALIZACAO = {
            'titulo', 'conteudo', 'versiculo_referencia', 'autor', 
            'categoria', 'tags', 'ativo', 'data_publicacao'
        }
        
        # Campos obrigatórios para criação
        self.CAMPOS_OBRIGATORIOS_CRIACAO = {
            'titulo', 'conteudo', 'versiculo_referencia', 'autor'
        }


    def criar_devocional(self, devocional_data: Dict[str, Any], user_id: int) -> Dict[str, Any]:
        """
        Cria um novo devocional aplicando todas as validações de negócio.
        
        Args:
            devocional_data: Dados do devocional a ser criado
            user_id: ID do usuário que está criando (para auditoria)
            
        Returns:
            Dict com dados do devocional criado
            
        Raises:
            BadRequest: Se dados inválidos
            Exception: Para erros internos
        """
        try:
            # 1. Validação de entrada (Single Responsibility)
            self._validar_dados_criacao(devocional_data)
            
            # 2. Sanitização e formatação dos dados
            devocional_sanitizado = self._sanitizar_dados_devocional(devocional_data)
            
            # 3. Aplicação de regras de negócio específicas
            devocional_processado = self._aplicar_regras_negocio_criacao(
                devocional_sanitizado, user_id
            )
            
            # 4. Criação no repository
            devocional_criado = self.devocional_repository.criar_devocional(devocional_processado)
            
            if not devocional_criado:
                raise Exception("Falha ao criar devocional no banco de dados")
            
            # 5. Log de auditoria
            self._log_operacao_sucesso("criar_devocional", user_id, devocional_criado.get('id'))
            
            return {
                "mensagem": "Devocional criado com sucesso",
                "devocional": devocional_criado,
                "status": "ativo"
            }
            
        except BadRequest:
            raise
        except Exception as e:
            self._log_operacao_erro("criar_devocional", user_id, str(e))
            current_app.logger.error(f"Erro ao criar devocional: {str(e)}")
            raise Exception("Falha interna ao criar devocional")


    def obter_devocional_por_id(self, devocional_id: int, user_id: Optional[int] = None) -> Dict[str, Any]:
        """
        Obtém um devocional específico por ID.
        
        Args:
            devocional_id: ID do devocional
            user_id: ID do usuário (para verificações de permissão)
            
        Returns:
            Dict com dados do devocional
            
        Raises:
            BadRequest: Se ID inválido
            NotFound: Se devocional não existe
        """
        try:
            # 1. Validação do ID
            if not isinstance(devocional_id, int) or devocional_id <= 0:
                raise BadRequest("ID de devocional inválido")
            
            # 2. Busca no repository
            devocional = self.devocional_repository.buscar_por_id(devocional_id)
            
            if not devocional:
                raise NotFound("Devocional não encontrado")
            
            # 3. Verificação de permissões (se necessário)
            if not self._usuario_pode_acessar_devocional(devocional, user_id):
                raise Unauthorized("Sem permissão para acessar este devocional")
            
            # 4. Formatação da resposta
            return self._formatar_resposta_devocional(devocional)
            
        except (BadRequest, NotFound, Unauthorized):
            raise
        except Exception as e:
            current_app.logger.error(f"Erro ao obter devocional {devocional_id}: {str(e)}")
            raise Exception("Falha interna ao obter devocional")


    def listar_devocionais(self, filtros: Dict[str, Any] = None, user_id: Optional[int] = None) -> Dict[str, Any]:
        """
        Lista devocionais com filtros opcionais.
        
        Args:
            filtros: Dicionário com filtros (categoria, data, autor, etc.)
            user_id: ID do usuário (para personalização)
            
        Returns:
            Dict com lista paginada de devocionais
        """
        try:
            # 1. Sanitização e validação dos filtros
            filtros_validados = self._validar_filtros_listagem(filtros or {})
            
            # 2. Aplicação de regras de negócio para listagem
            filtros_processados = self._aplicar_regras_listagem(filtros_validados, user_id)
            
            # 3. Busca no repository
            resultado = self.devocional_repository.listar_devocionais(filtros_processados)
            
            # 4. Formatação da resposta
            return {
                "devocionais": [self._formatar_devocional_resumo(d) for d in resultado['devocionais']],
                "total": resultado['total'],
                "pagina": resultado.get('pagina', 1),
                "por_pagina": resultado.get('por_pagina', 10)
            }
            
        except Exception as e:
            current_app.logger.error(f"Erro ao listar devocionais: {str(e)}")
            raise Exception("Falha interna ao listar devocionais")


    def atualizar_devocional(self, devocional_id: int, dados_atualizacao: Dict[str, Any], user_id: int) -> Tuple[Dict[str, Any], int]:
        """
        Atualiza um devocional existente.
        
        Args:
            devocional_id: ID do devocional
            dados_atualizacao: Dados para atualização
            user_id: ID do usuário que está atualizando
            
        Returns:
            Tuple (resposta, status_code)
        """
        try:
            # 1. Validação do ID
            if not isinstance(devocional_id, int) or devocional_id <= 0:
                return {"erro": "ID de devocional inválido"}, 400
            
            # 2. Verificação de existência e permissões
            devocional_existente = self.devocional_repository.buscar_por_id(devocional_id)
            if not devocional_existente:
                return {"erro": "Devocional não encontrado"}, 404
            
            if not self._usuario_pode_editar_devocional(devocional_existente, user_id):
                return {"erro": "Sem permissão para editar este devocional"}, 403
            
            # 3. Validação e sanitização dos dados
            dados_validados = self._validar_dados_atualizacao(dados_atualizacao)
            
            if not dados_validados:
                return {"erro": "Nenhum campo válido para atualização"}, 400
            
            # 4. Aplicação de regras de negócio
            dados_processados = self._aplicar_regras_negocio_atualizacao(
                dados_validados, devocional_existente, user_id
            )
            
            # 5. Atualização no repository
            resultado = self.devocional_repository.atualizar_devocional(devocional_id, dados_processados)
            
            # 6. Log de auditoria
            self._log_operacao_sucesso("atualizar_devocional", user_id, devocional_id)
            
            return resultado
            
        except Exception as e:
            self._log_operacao_erro("atualizar_devocional", user_id, str(e))
            current_app.logger.error(f"Erro ao atualizar devocional {devocional_id}: {str(e)}")
            return {"erro": "Falha interna ao atualizar devocional"}, 500


    def deletar_devocional(self, devocional_id: int, user_id: int) -> Tuple[Dict[str, Any], int]:
        """
        Deleta um devocional (soft delete).
        
        Args:
            devocional_id: ID do devocional
            user_id: ID do usuário que está deletando
            
        Returns:
            Tuple (resposta, status_code)
        """
        try:
            # 1. Validação do ID
            if not isinstance(devocional_id, int) or devocional_id <= 0:
                return {"erro": "ID de devocional inválido"}, 400
            
            # 2. Verificação de existência e permissões
            devocional = self.devocional_repository.buscar_por_id(devocional_id)
            if not devocional:
                return {"erro": "Devocional não encontrado"}, 404
            
            if not self._usuario_pode_deletar_devocional(devocional, user_id):
                return {"erro": "Sem permissão para deletar este devocional"}, 403
            
            # 3. Soft delete no repository
            resultado = self.devocional_repository.deletar_devocional(devocional_id, user_id)
            
            # 4. Log de auditoria
            self._log_operacao_sucesso("deletar_devocional", user_id, devocional_id)
            
            return resultado
            
        except Exception as e:
            self._log_operacao_erro("deletar_devocional", user_id, str(e))
            current_app.logger.error(f"Erro ao deletar devocional {devocional_id}: {str(e)}")
            return {"erro": "Falha interna ao deletar devocional"}, 500


    def obter_devocional_do_dia(self, user_id: Optional[int] = None) -> Dict[str, Any]:
        """
        Obtém o devocional específico para o dia atual.
        
        Args:
            user_id: ID do usuário (para personalização)
            
        Returns:
            Dict com devocional do dia
        """
        try:
            data_hoje = date.today()
            
            # 1. Busca devocional específico para hoje
            devocional = self.devocional_repository.buscar_por_data(data_hoje)
            
            # 2. Se não encontrar, busca o mais recente ativo
            if not devocional:
                devocional = self.devocional_repository.buscar_mais_recente_ativo()
            
            if not devocional:
                raise NotFound("Nenhum devocional disponível para hoje")
            
            # 3. Formatação da resposta
            return self._formatar_resposta_devocional(devocional)
            
        except NotFound:
            raise
        except Exception as e:
            current_app.logger.error(f"Erro ao obter devocional do dia: {str(e)}")
            raise Exception("Falha interna ao obter devocional do dia")


    # ================================
    # MÉTODOS PRIVADOS (Single Responsibility)
    # ================================

    def _validar_dados_criacao(self, dados: Dict[str, Any]) -> None:
        """Valida dados para criação de devocional."""
        if not isinstance(dados, dict):
            raise BadRequest("Dados devem ser um objeto JSON válido")
        
        campos_faltantes = self.CAMPOS_OBRIGATORIOS_CRIACAO - dados.keys()
        if campos_faltantes:
            raise BadRequest(f"Campos obrigatórios faltando: {', '.join(campos_faltantes)}")
        
        # Validações específicas
        if not dados.get('titulo') or len(dados['titulo'].strip()) < 3:
            raise BadRequest("Título deve ter pelo menos 3 caracteres")
        
        if not dados.get('conteudo') or len(dados['conteudo'].strip()) < 10:
            raise BadRequest("Conteúdo deve ter pelo menos 10 caracteres")


    def _validar_dados_atualizacao(self, dados: Dict[str, Any]) -> Dict[str, Any]:
        """Valida e filtra dados para atualização."""
        if not isinstance(dados, dict):
            raise BadRequest("Dados devem ser um objeto JSON válido")
        
        # Filtra apenas campos permitidos
        dados_validados = {
            campo: valor 
            for campo, valor in dados.items() 
            if campo in self.CAMPOS_PERMITIDOS_ATUALIZACAO and valor is not None
        }
        
        # Validações específicas para campos presentes
        if 'titulo' in dados_validados and len(dados_validados['titulo'].strip()) < 3:
            raise BadRequest("Título deve ter pelo menos 3 caracteres")
        
        if 'conteudo' in dados_validados and len(dados_validados['conteudo'].strip()) < 10:
            raise BadRequest("Conteúdo deve ter pelo menos 10 caracteres")
        
        return dados_validados


    def _sanitizar_dados_devocional(self, dados: Dict[str, Any]) -> Dict[str, Any]:
        """Sanitiza e formata dados do devocional."""
        dados_sanitizados = dados.copy()
        
        # Sanitização de strings
        if 'titulo' in dados_sanitizados:
            dados_sanitizados['titulo'] = dados_sanitizados['titulo'].strip()
        
        if 'conteudo' in dados_sanitizados:
            dados_sanitizados['conteudo'] = dados_sanitizados['conteudo'].strip()
        
        if 'autor' in dados_sanitizados:
            dados_sanitizados['autor'] = dados_sanitizados['autor'].strip()
        
        # Formatação de tags
        if 'tags' in dados_sanitizados and isinstance(dados_sanitizados['tags'], str):
            dados_sanitizados['tags'] = [tag.strip() for tag in dados_sanitizados['tags'].split(',')]
        
        return dados_sanitizados


    def _aplicar_regras_negocio_criacao(self, dados: Dict[str, Any], user_id: int) -> Dict[str, Any]:
        """Aplica regras de negócio específicas para criação."""
        dados_processados = dados.copy()
        
        # Adiciona metadados de criação
        dados_processados['criado_por'] = user_id
        dados_processados['data_criacao'] = datetime.now()
        
        # Define valores padrão
        dados_processados.setdefault('ativo', True)
        dados_processados.setdefault('categoria', 'geral')
        dados_processados.setdefault('data_publicacao', date.today())
        
        return dados_processados


    def _aplicar_regras_negocio_atualizacao(self, dados: Dict[str, Any], devocional_existente: Dict[str, Any], user_id: int) -> Dict[str, Any]:
        """Aplica regras de negócio específicas para atualização."""
        dados_processados = dados.copy()
        
        # Adiciona metadados de atualização
        dados_processados['atualizado_por'] = user_id
        dados_processados['data_atualizacao'] = datetime.now()
        
        return dados_processados


    def _validar_filtros_listagem(self, filtros: Dict[str, Any]) -> Dict[str, Any]:
        """Valida e sanitiza filtros para listagem."""
        filtros_validados = {}
        
        # Filtros permitidos
        if 'categoria' in filtros:
            filtros_validados['categoria'] = str(filtros['categoria']).strip()
        
        if 'autor' in filtros:
            filtros_validados['autor'] = str(filtros['autor']).strip()
        
        if 'ativo' in filtros:
            filtros_validados['ativo'] = bool(filtros['ativo'])
        
        # Paginação
        if 'pagina' in filtros:
            try:
                filtros_validados['pagina'] = max(1, int(filtros['pagina']))
            except (ValueError, TypeError):
                filtros_validados['pagina'] = 1
        
        if 'por_pagina' in filtros:
            try:
                filtros_validados['por_pagina'] = min(100, max(1, int(filtros['por_pagina'])))
            except (ValueError, TypeError):
                filtros_validados['por_pagina'] = 10
        
        return filtros_validados


    def _aplicar_regras_listagem(self, filtros: Dict[str, Any], user_id: Optional[int]) -> Dict[str, Any]:
        """Aplica regras de negócio para listagem."""
        filtros_processados = filtros.copy()
        
        # Por padrão, mostra apenas devocionais ativos para usuários comuns
        if user_id and not self._usuario_e_admin(user_id):
            filtros_processados['ativo'] = True
        
        return filtros_processados


    def _usuario_pode_acessar_devocional(self, devocional: Dict[str, Any], user_id: Optional[int]) -> bool:
        """Verifica se usuário pode acessar o devocional."""
        # Devocionais ativos são públicos
        if devocional.get('ativo', False):
            return True
        
        # Criador ou admin podem acessar devocionais inativos
        if user_id:
            return (devocional.get('criado_por') == user_id or 
                   self._usuario_e_admin(user_id))
        
        return False


    def _usuario_pode_editar_devocional(self, devocional: Dict[str, Any], user_id: int) -> bool:
        """Verifica se usuário pode editar o devocional."""
        return (devocional.get('criado_por') == user_id or 
               self._usuario_e_admin(user_id))


    def _usuario_pode_deletar_devocional(self, devocional: Dict[str, Any], user_id: int) -> bool:
        """Verifica se usuário pode deletar o devocional."""
        return (devocional.get('criado_por') == user_id or 
               self._usuario_e_admin(user_id))


    def _usuario_e_admin(self, user_id: int) -> bool:
        """Verifica se usuário é administrador."""
        # TODO: Implementar lógica de verificação de admin
        # Por enquanto, retorna False
        return False


    def _formatar_resposta_devocional(self, devocional: Dict[str, Any]) -> Dict[str, Any]:
        """Formata resposta completa do devocional."""
        return {
            "id": devocional.get('id'),
            "titulo": devocional.get('titulo'),
            "conteudo": devocional.get('conteudo'),
            "versiculo_referencia": devocional.get('versiculo_referencia'),
            "autor": devocional.get('autor'),
            "categoria": devocional.get('categoria'),
            "tags": devocional.get('tags', []),
            "data_publicacao": devocional.get('data_publicacao'),
            "ativo": devocional.get('ativo', True)
        }


    def _formatar_devocional_resumo(self, devocional: Dict[str, Any]) -> Dict[str, Any]:
        """Formata resposta resumida do devocional para listagem."""
        return {
            "id": devocional.get('id'),
            "titulo": devocional.get('titulo'),
            "autor": devocional.get('autor'),
            "categoria": devocional.get('categoria'),
            "data_publicacao": devocional.get('data_publicacao'),
            "preview": devocional.get('conteudo', '')[:150] + '...' if devocional.get('conteudo') else ''
        }


    def _log_operacao_sucesso(self, operacao: str, user_id: int, devocional_id: Optional[int] = None) -> None:
        """Log de operações bem-sucedidas."""
        current_app.logger.info(
            f"[DEVOCIONAL SUCCESS] {operacao} | User: {user_id} | Devocional: {devocional_id}"
        )


    def _log_operacao_erro(self, operacao: str, user_id: int, erro: str) -> None:
        """Log de operações com erro."""
        current_app.logger.error(
            f"[DEVOCIONAL ERROR] {operacao} | User: {user_id} | Error: {erro[:200]}"
        )