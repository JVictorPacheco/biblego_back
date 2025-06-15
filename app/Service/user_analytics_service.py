from app.Repository.usuario_repository import UsuarioRepository
from flask import current_app

class UserAnalyticsService:
    def __init__(self):
        self.usuario_repo = UsuarioRepository()
    
    def obter_estatisticas_login(self):
        """Obtém estatísticas gerais de login - Camada de negócio"""
        try:
            stats = self.usuario_repo.buscar_estatisticas_login_geral()
            
            if not stats:
                raise ValueError("Não foi possível obter estatísticas")
            
            # Aqui você pode adicionar lógica de negócio adicional
            # como cálculos, formatações, validações, etc.
            
            # Exemplo: adicionar taxa de engajamento
            if stats['total_usuarios'] > 0:
                stats['taxa_usuarios_ativos'] = round(
                    (stats['usuarios_com_login'] / stats['total_usuarios']) * 100, 2
                )
                stats['taxa_engajamento_semanal'] = round(
                    (stats['logins_ultima_semana'] / stats['usuarios_com_login']) * 100, 2
                ) if stats['usuarios_com_login'] > 0 else 0
            else:
                stats['taxa_usuarios_ativos'] = 0
                stats['taxa_engajamento_semanal'] = 0
            
            current_app.logger.info(f"Estatísticas de login obtidas: {stats['logins_hoje']} logins hoje")
            
            return stats
            
        except Exception as e:
            current_app.logger.error(f"Erro ao obter estatísticas de login: {str(e)}")
            raise
    
    def obter_info_login_usuario(self, user_id):
        """Obtém informações de login de um usuário específico"""
        try:
            # Validação de entrada
            if not isinstance(user_id, int) or user_id <= 0:
                raise ValueError("ID de usuário inválido")
            
            login_info = self.usuario_repo.buscar_info_login(user_id)
            
            if not login_info:
                raise ValueError("Usuário não encontrado")
            
            # Lógica de negócio adicional
            if login_info['tem_login_anterior']:
                # Calcula dias desde primeiro login
                if login_info['primeiro_login']:
                    from datetime import datetime
                    dias_desde_primeiro_login = (
                        datetime.now() - login_info['primeiro_login']
                    ).days
                    login_info['dias_como_usuario'] = dias_desde_primeiro_login
                    
                # Calcula tempo desde último login
                if login_info['ultimo_login']:
                    tempo_desde_ultimo = (
                        datetime.now() - login_info['ultimo_login']
                    ).total_seconds()
                    login_info['segundos_desde_ultimo_login'] = int(tempo_desde_ultimo)
            
            # Converte timestamps para ISO format
            if login_info['primeiro_login']:
                login_info['primeiro_login'] = login_info['primeiro_login'].isoformat()
            if login_info['ultimo_login']:
                login_info['ultimo_login'] = login_info['ultimo_login'].isoformat()
            
            return login_info
            
        except ValueError:
            # Re-lança erros de validação
            raise
        except Exception as e:
            current_app.logger.error(f"Erro ao obter info de login do usuário {user_id}: {str(e)}")
            raise
    
    def obter_usuario_completo(self, user_id, incluir_login_info=False):
        """Obtém dados completos do usuário com opção de incluir info de login"""
        try:
            if not isinstance(user_id, int) or user_id <= 0:
                raise ValueError("ID de usuário inválido")
            
            usuario = self.usuario_repo.buscar_usuario_por_id(user_id, incluir_login_info)
            
            if not usuario:
                raise ValueError("Usuário não encontrado")
            
            # Aqui você pode adicionar lógica de negócio
            # como mascarar dados sensíveis, calcular campos derivados, etc.
            
            return usuario
            
        except ValueError:
            raise
        except Exception as e:
            current_app.logger.error(f"Erro ao obter usuário completo {user_id}: {str(e)}")
            raise