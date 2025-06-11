from typing import Optional, List
from flask import current_app
import json
import psycopg2
from psycopg2.extras import RealDictCursor
from app.Models.token_audit import TokenAuditCreate, TokenAudit
from app.Config.audit_database import AuditDatabase

class TokenAuditRepository:
    
    @staticmethod
    def create(audit_data: TokenAuditCreate) -> Optional[TokenAudit]:
        """Versão final usando pool dedicado"""
        conn = None
        cursor = None
        try:
            conn = AuditDatabase.get_connection()
            cursor = conn.cursor()
            
            query = """
                INSERT INTO tokens_audit_log (
                    user_id, token_type, action, token_jti,
                    error, ip_address, user_agent
                ) VALUES (%s, %s, %s, %s, %s, %s, %s)
                RETURNING id, timestamp
            """
            
            # Prepara os valores garantindo que não são None
            values = (
                audit_data.user_id,
                audit_data.token_type,
                audit_data.action,
                audit_data.token_jti if audit_data.token_jti else None,
                audit_data.error if audit_data.error else None,
                audit_data.ip_address if audit_data.ip_address else None,
                audit_data.user_agent if audit_data.user_agent else None
            )
            
            cursor.execute(query, values)
            result = cursor.fetchone()
            conn.commit()
            
            if result:
                return TokenAudit(
                    id=result[0],
                    timestamp=result[1],
                    **audit_data.dict(exclude_none=True)
                )
            return None
            
        except psycopg2.Error as e:
            current_app.logger.error(
                f"AUDIT DB ERROR | {audit_data.action if hasattr(audit_data, 'action') else 'unknown'} | "
                f"Code: {e.pgcode} | Error: {e.pgerror}"
            )
            if conn:
                conn.rollback()
            return None
        except Exception as e:
            current_app.logger.error(
                f"AUDIT UNKNOWN ERROR | {audit_data.action if hasattr(audit_data, 'action') else 'unknown'} | "
                f"Error: {str(e)[:200]}"
            )
            return None
        finally:
            if cursor:
                cursor.close()
            if conn:
                AuditDatabase.release_connection(conn)
                    
    @staticmethod
    def get_by_user(user_id: str, limit: int = 100) -> List[TokenAudit]:
        """Obtém registros de auditoria para um usuário específico"""
        conn = None
        cursor = None
        try:
            conn = AuditDatabase.get_connection()
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            
            query = """
                SELECT id, timestamp, user_id, token_type, action,
                    token_jti, error, ip_address, user_agent
                FROM tokens_audit_log
                WHERE user_id = %s
                ORDER BY timestamp DESC
                LIMIT %s
            """
            
            cursor.execute(query, (user_id, limit))
            results = []
            
            for row in cursor.fetchall():
                results.append(
                    TokenAudit(
                        id=row['id'],
                        timestamp=row['timestamp'],
                        user_id=row['user_id'],
                        token_type=row['token_type'],
                        action=row['action'],
                        token_jti=row['token_jti'],
                        error=row['error'],
                        ip_address=row['ip_address'],
                        user_agent=row['user_agent']
                    )
                )
            
            return results
            
        except psycopg2.Error as e:
            current_app.logger.error(f"Database error while fetching audit logs: {e}")
            return []
        except Exception as e:
            current_app.logger.error(f"Unexpected error fetching audit logs: {str(e)}")
            return []
        finally:
            if cursor:
                cursor.close()
            if conn:
                AuditDatabase.release_connection(conn)