from typing import Optional, List, Dict, Any, Tuple
from datetime import datetime, date
from app.Repository.devotionals_repository import DevotionalsRepository
from app.Models.devotional import Devotional, DevotionalCreate, DevotionalUpdate
from werkzeug.exceptions import BadRequest, NotFound, Unauthorized
from flask import current_app
import traceback




class DevocionalService:
    """
    Service responsável pela lógica de negócio dos devocionais.
    Aplica princípios SOLID e Clean Code para separar responsabilidades.
    """
    
    def __init__(self, devocional_repository: DevotionalsRepository = None):
        """
        Inicializa o service com injeção de dependência.
        
        Args:
            devocional_repository: Repository para operações de dados (Dependency Injection)
        """
        self.devocional_repository = devocional_repository or DevotionalsRepository()
        
        # Campos permitidos para atualização (Princípio da Responsabilidade Única)
        self.CAMPOS_PERMITIDOS_ATUALIZACAO = {
            'titulo', 'conteudo', 'versiculo_referencia', 'autor', 
            'categoria', 'tags', 'ativo', 'data_publicacao'
        }
        
        # Campos obrigatórios para criação
        self.CAMPOS_OBRIGATORIOS_CRIACAO = {
            'titulo', 'conteudo', 'versiculo_referencia', 'autor'
        }


    def criar_devocional(self, devocional_data: Dict[str, Any], user_id: int) -> Tuple[Dict[str, Any], int]:
        """
        Cria um novo devocional (versão com debug COMPLETO)
        """
        try:
            # 1. VALIDAÇÃO INICIAL
            print(f"[SERVICE DEBUG 1] Dados recebidos: {type(devocional_data)}")
            print(f"[SERVICE DEBUG 1] User ID: {user_id}")
            print(f"[SERVICE DEBUG 1] Primeiros campos: {list(devocional_data.keys())[:5] if devocional_data else 'None'}")
            
            if devocional_data is None:
                current_app.logger.error("devocional_data é None")
                return {"erro": "Dados do devocional não foram fornecidos"}, 400
            
            if not isinstance(devocional_data, dict):
                current_app.logger.error(f"devocional_data não é dict: {type(devocional_data)}")
                return {"erro": "Dados devem ser um objeto JSON válido"}, 400
            
            if not devocional_data:
                return {"erro": "Dados do devocional não podem estar vazios"}, 400
            
            # 2. VALIDAÇÃO DETALHADA
            print(f"[SERVICE DEBUG 2] Antes da validação: {type(devocional_data)}")
            self._validar_dados_criacao(devocional_data)
            print(f"[SERVICE DEBUG 2] Após validação: {type(devocional_data)}")
            
            # 3. SANITIZAÇÃO
            print(f"[SERVICE DEBUG 3] Antes sanitização: {type(devocional_data)}")
            devocional_sanitizado = self._sanitizar_dados_devocional(devocional_data)
            print(f"[SERVICE DEBUG 3] Após sanitização: {type(devocional_sanitizado)}")
            print(f"[SERVICE DEBUG 3] Dados sanitizados é None? {devocional_sanitizado is None}")
            print(f"[SERVICE DEBUG 3] Campos sanitizados: {list(devocional_sanitizado.keys()) if devocional_sanitizado else 'None'}")
            
            # 4. REGRAS DE NEGÓCIO
            print(f"[SERVICE DEBUG 4] Antes regras negócio: {type(devocional_sanitizado)}")
            devocional_processado = self._aplicar_regras_negocio_criacao(devocional_sanitizado, user_id)
            print(f"[SERVICE DEBUG 4] Após regras negócio: {type(devocional_processado)}")
            print(f"[SERVICE DEBUG 4] Dados processados é None? {devocional_processado is None}")
            print(f"[SERVICE DEBUG 4] Campos processados: {list(devocional_processado.keys()) if devocional_processado else 'None'}")
            
            # 5. VERIFICAÇÃO FINAL ANTES DO REPOSITORY
            if devocional_processado is None:
                print("[SERVICE DEBUG 5] ERRO: devocional_processado é None!")
                return {"erro": "Erro no processamento dos dados"}, 500
            
            print(f"[SERVICE DEBUG 5] Enviando para repository: {type(devocional_processado)}")
            print(f"[SERVICE DEBUG 5] Últimos campos: {list(devocional_processado.keys())[-5:] if devocional_processado else 'None'}")
            
            # 6. CRIAÇÃO NO REPOSITORY
            devocional_id = self.devocional_repository.criar_devocional(devocional_processado)
            
            if not devocional_id:
                return {"erro": "Falha ao criar devocional no banco de dados"}, 500
            
            return {
                "mensagem": "Devocional criado com sucesso",
                "id": devocional_id,
                "titulo": devocional_processado.get('title')
            }, 201
            
        except ValueError as e:
            print(f"[SERVICE DEBUG ERROR] ValueError: {str(e)}")
            current_app.logger.warning(f"Dados inválidos: {str(e)}")
            return {"erro": str(e)}, 400
        except Exception as e:
            print(f"[SERVICE DEBUG ERROR] Exception: {str(e)}")
            print(f"[SERVICE DEBUG ERROR] Traceback: {traceback.format_exc()}")
            current_app.logger.error(f"Erro ao criar devocional: {str(e)}")
            return {"erro": "Falha interna ao criar devocional"}, 500


    def obter_devocional_por_id(self, devocional_id: int, user_id: Optional[int] = None) -> Dict[str, Any]:
        """
        Deleta um devocional usando SUA função buscar_devocional_por_id
        """
        try:
            print(f"[SERVICE DEBUG] Deletando devocional {devocional_id} por usuário {user_id}")
            
            # 1. Validação do ID
            if not isinstance(devocional_id, int) or devocional_id <= 0:
                return {"erro": "ID de devocional inválido"}, 400
            
            # 2. Buscar devocional usando SUA função
            devocional = self.devocional_repository.buscar_devocional_por_id(devocional_id)
            
            if not devocional:
                return {"erro": "Devocional não encontrado"}, 404
            
            print(f"[SERVICE DEBUG] Devocional encontrado: {devocional.get('title')}")
            print(f"[SERVICE DEBUG] Autor: {devocional.get('author')}")
            
            # 3. OPCIONAL: Verificar se usuário pode deletar
            # (Exemplo: só o autor pode deletar, ou qualquer usuário logado)
            # if devocional.get('created_by') != user_id:  # Se tivesse campo created_by
            #     return {"erro": "Sem permissão para deletar este devocional"}, 403
            
            # 4. Deletar no repository
            sucesso = self.devocional_repository.deletar_devocional(devocional_id)
            
            if not sucesso:
                return {"erro": "Falha ao deletar devocional"}, 500
            
            # 5. Log de sucesso
            current_app.logger.info(f"Devocional '{devocional.get('title')}' (ID: {devocional_id}) deletado por usuário {user_id}")
            
            return {
                "mensagem": "Devocional deletado com sucesso",
                "id": devocional_id,
                "titulo": devocional.get('title')  # ← Informação extra graças à sua função!
            }, 200
            
        except Exception as e:
            current_app.logger.error(f"Erro ao deletar devocional {devocional_id}: {str(e)}")
            return {"erro": "Falha interna ao deletar devocional"}, 500


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
            filtros = filtros or {}
            pagina = filtros.get('pagina', 1)
            por_pagina = filtros.get('por_pagina', 10)
            
            # ✅ USA O REPOSITORY EXISTENTE
            resultado = DevotionalsRepository.listar_devocionais_paginado(
                page=pagina, 
                per_page=por_pagina
            )
            
            return {
                "devocionais": resultado['devocionais'],
                "total": resultado['pagination']['total'],
                "pagina": resultado['pagination']['page'],
                "por_pagina": resultado['pagination']['per_page']
            }
        except Exception as e:
            current_app.logger.error(f"Erro ao listar devocionais: {str(e)}")
            raise Exception("Falha interna ao listar devocionais")
        
   
        
        # try:
        #     # 1. Sanitização e validação dos filtros
        #     filtros_validados = self._validar_filtros_listagem(filtros or {})
            
        #     # 2. Aplicação de regras de negócio para listagem
        #     filtros_processados = self._aplicar_regras_listagem(filtros_validados, user_id)
            
        #     # 3. Busca no repository
        #     resultado = self.devocional_repository.buscar_devocional_do_dia(filtros_processados)
            
        #     # 4. Formatação da resposta
        #     return {
        #         "devocionais": [self._formatar_devocional_resumo(d) for d in resultado['devocionais']],
        #         "total": resultado['total'],
        #         "pagina": resultado.get('pagina', 1),
        #         "por_pagina": resultado.get('por_pagina', 10)
        #     }
            
        # except Exception as e:
        #     current_app.logger.error(f"Erro ao listar devocionais: {str(e)}")
        #     raise Exception("Falha interna ao listar devocionais")


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
            devocional_existente = self.devocional_repository.buscar_devocional_por_id(devocional_id)
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


    def deletar_devocional_interno(self, devocional_id: int) -> Tuple[Dict[str, Any], int]:
        """Deleta um devocional - método interno para desenvolvedor"""
        try:
            print(f"[DEV SERVICE] Deletando devocional {devocional_id}")
            
            if not isinstance(devocional_id, int) or devocional_id <= 0:
                return {"erro": "ID inválido"}, 400
            
            # Buscar primeiro para obter dados
            devocional = self.devocional_repository.buscar_devocional_por_id(devocional_id)
            if not devocional:
                return {"erro": "Devocional não encontrado"}, 404
            
            # Deletar
            sucesso = self.devocional_repository.deletar_devocional(devocional_id)
            if not sucesso:
                return {"erro": "Falha ao deletar no banco"}, 500
            
            print(f"[DEV SERVICE] ✅ Deletado: '{devocional.get('title')}'")
            
            return {
                "mensagem": "Devocional deletado com sucesso",
                "id": devocional_id,
                "titulo": devocional.get('title'),
                "autor": devocional.get('author'),
                "modo": "interno_desenvolvedor"
            }, 200
            
        except Exception as e:
            print(f"[DEV SERVICE] ❌ Erro: {e}")
            return {"erro": "Falha interna"}, 500


    def buscar_por_criterios(self, titulo: str = "", autor: str = "") -> List[Dict[str, Any]]:
        """Busca devocionais por critérios"""
        try:
            print(f"[DEV SERVICE] Buscando: titulo='{titulo}', autor='{autor}'")
            devocionais = self.devocional_repository.buscar_por_criterios_dev(titulo, autor)
            print(f"[DEV SERVICE] Encontrados: {len(devocionais)}")
            return devocionais
        except Exception as e:
            print(f"[DEV SERVICE] Erro na busca: {e}")
            return []


    def obter_devocional_do_dia(self, data_referencia: Optional[date] = None) -> Dict[str, Any]:
        """
        Obtém devocional seguindo regras de negócio específicas
        
        REGRAS:
        1. Busca exato para a data
        2. Se não encontrar, busca período próximo (7 dias)
        3. Último recurso: mais recente até hoje (sem futuro)
        """
        try:
            if data_referencia is None:
                data_referencia = date.today()
                
            current_app.logger.info(f"Buscando devocional para: {data_referencia}")
            
            # REGRA 1: Busca exata
            devocional_exato = self.devocional_repository.buscar_devocional_do_dia(data_referencia)
            
            if devocional_exato:
                current_app.logger.info(f"Devocional exato encontrado: ID {devocional_exato['id']}")
                return {
                    "devocional": devocional_exato,
                    "tipo_busca": "exato",
                    "data_solicitada": data_referencia
                }
            
            # REGRA 2: Período próximo
            current_app.logger.info("Buscando período próximo")
            devocionais_periodo = self.devocional_repository.buscar_devocional_periodo_ate_hoje(7)
            
            if devocionais_periodo:
                devocional_periodo = devocionais_periodo[0]
                current_app.logger.info(f"Devocional do período: ID {devocional_periodo['id']}")
                return {
                    "devocional": devocional_periodo,
                    "tipo_busca": "periodo_proximo",
                    "data_solicitada": data_referencia,
                    "mensagem": "Devocional do período mais próximo"
                }
            
            # REGRA 3: Mais recente geral (sem futuro)
            current_app.logger.info("Buscando mais recente até hoje")
            devocional_recente = self.devocional_repository.buscar_devocional_mais_recente_ate_hoje()
            
            if devocional_recente:
                current_app.logger.info(f"Mais recente encontrado: ID {devocional_recente['id']}")
                return {
                    "devocional": devocional_recente,
                    "tipo_busca": "mais_recente",
                    "data_solicitada": data_referencia,
                    "mensagem": "Devocional mais recente disponível"
                }
            
            # REGRA 4: Nenhum encontrado
            raise NotFound("Nenhum devocional disponível")
            
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
            """
            Sanitiza dados (versão com debug)
            """
            # print(f"[SANITIZAR DEBUG 1] Entrada: {type(dados)}")
            # print(f"[SANITIZAR DEBUG 1] É None? {dados is None}")
            
            # VERIFICAÇÃO CRÍTICA
            if dados is None:
                # print("[SANITIZAR DEBUG ERROR] Dados são None!")
                raise ValueError("Dados para sanitização são None")
            
            if not isinstance(dados, dict):
                # print(f"[SANITIZAR DEBUG ERROR] Dados não são dict: {type(dados)}")
                raise ValueError(f"Dados devem ser um dicionário, recebido: {type(dados)}")
            
            # print(f"[SANITIZAR DEBUG 2] Copiando dados...")
            
            try:
                dados_sanitizados = dados.copy()
                print(f"[SANITIZAR DEBUG 2] Cópia feita: {type(dados_sanitizados)}")
            except Exception as e:
                print(f"[SANITIZAR DEBUG ERROR] Erro ao copiar: {e}")
                raise ValueError(f"Erro ao copiar dados: {e}")
            
            # Sanitização de strings
            campos_string = ['title', 'main_verse', 'verse_reference', 'content', 
                            'application', 'prayer', 'author', 'tags']
            
            for campo in campos_string:
                if campo in dados_sanitizados:
                    valor = dados_sanitizados[campo]
                    if valor is not None and isinstance(valor, str):
                        dados_sanitizados[campo] = valor.strip()
            
            # Conversão de data
            if 'publish_date' in dados_sanitizados:
                valor_data = dados_sanitizados['publish_date']
                if isinstance(valor_data, str):
                    try:
                        from datetime import datetime
                        dados_sanitizados['publish_date'] = datetime.strptime(valor_data, '%Y-%m-%d').date()
                    except ValueError as e:
                        raise ValueError(f"Formato de data inválido: {e}")
            
            # print(f"[SANITIZAR DEBUG 3] Saída: {type(dados_sanitizados)}")
            # print(f"[SANITIZAR DEBUG 3] Retornando None? {dados_sanitizados is None}")
            
            return dados_sanitizados
    

    def _aplicar_regras_negocio_criacao(self, dados: Dict[str, Any], user_id: int) -> Dict[str, Any]:
            """
            Aplica regras de negócio (versão com debug)
            """
            # print(f"[REGRAS DEBUG 1] Entrada: {type(dados)}")
            # print(f"[REGRAS DEBUG 1] É None? {dados is None}")
            # print(f"[REGRAS DEBUG 1] User ID: {user_id}")
            
            if dados is None:
                print("[REGRAS DEBUG ERROR] Dados são None!")
                raise ValueError("Dados para regras de negócio são None")
            
            try:
                dados_processados = dados.copy()
                print(f"[REGRAS DEBUG 2] Cópia feita: {type(dados_processados)}")
            except Exception as e:
                print(f"[REGRAS DEBUG ERROR] Erro ao copiar: {e}")
                raise ValueError(f"Erro ao copiar dados: {e}")
            
            # Validação de campos obrigatórios
            campos_obrigatorios = [
                'title', 'main_verse', 'verse_reference', 'book_id',
                'chapter', 'verse', 'content', 'application',
                'prayer', 'author', 'publish_date', 'tags'
            ]
            
            for campo in campos_obrigatorios:
                if campo not in dados_processados or not dados_processados[campo]:
                    raise ValueError(f"Campo obrigatório '{campo}' está ausente ou vazio")
            
            # Define data de publicação se necessário
            if 'publish_date' not in dados_processados:
                from datetime import date
                dados_processados['publish_date'] = date.today()
            
            # print(f"[REGRAS DEBUG 3] Saída: {type(dados_processados)}")
            # print(f"[REGRAS DEBUG 3] Retornando None? {dados_processados is None}")
            
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


    def _validar_dados_criacao(self, devocional_data: Dict[str, Any]) -> None:
        """
        Valida os dados básicos de entrada para criação de devocional.
        Args:
            devocional_data: Dados do devocional a serem validados
        Raises:
            ValueError: Se algum dado for inválido
        """
        if not devocional_data:
            raise ValueError("Dados do devocional não podem estar vazios")
        
        # Validação de tipos básicos
        campos_string = ['title', 'main_verse', 'verse_reference', 'content', 
                        'application', 'prayer', 'author', 'tags']
        
        for campo in campos_string:
            if campo in devocional_data:
                if not isinstance(devocional_data[campo], str):
                    raise ValueError(f"Campo '{campo}' deve ser uma string")
                if not devocional_data[campo].strip():
                    raise ValueError(f"Campo '{campo}' não pode estar vazio")
        
        # Validação de campos numéricos
        campos_numericos = ['book_id', 'chapter', 'verse']
        for campo in campos_numericos:
            if campo in devocional_data:
                if not isinstance(devocional_data[campo], int):
                    raise ValueError(f"Campo '{campo}' deve ser um número inteiro")
                if devocional_data[campo] <= 0:
                    raise ValueError(f"Campo '{campo}' deve ser maior que zero")
        
        # Validação específica para book_id
        if 'book_id' in devocional_data:
            if devocional_data['book_id'] < 1 or devocional_data['book_id'] > 66:
                raise ValueError("book_id deve estar entre 1 e 66 (livros da Bíblia)")
        
        # Validação de data
        if 'publish_date' in devocional_data:
            if isinstance(devocional_data['publish_date'], str):
                try:
                    from datetime import datetime
                    datetime.strptime(devocional_data['publish_date'], '%Y-%m-%d')
                except ValueError:
                    raise ValueError("publish_date deve estar no formato YYYY-MM-DD")
        
        print(f"[DEBUG] Validação de dados passou para: {list(devocional_data.keys())}")


    def verificar_devocional_existe(self, devocional_id: int) -> bool:
        """
        Verifica se um devocional existe (método auxiliar)
        Args:
            devocional_id: ID do devocional
        Returns:
            True se existe, False caso contrário
        """
        try:
            devocional = self.devocional_repository.buscar_devocional_por_id(devocional_id)
            return devocional is not None
        except Exception as e:
            print(f"[DEV SERVICE] ❌ Erro ao verificar existência: {e}")
            return False    


    def _log_operacao_erro(self, operacao: str, user_id: int, erro: str) -> None:
        """Log de operações com erro."""
        current_app.logger.error(
            f"[DEVOCIONAL ERROR] {operacao} | User: {user_id} | Error: {erro[:200]}"
        )