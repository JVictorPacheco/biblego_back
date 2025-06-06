from typing import List, Optional, Dict, Any
from app.Models.token_audit import TokenAudit, TokenAuditCreate
import json
import psycopg2
from psycopg2.extras import RealDictCursor
from app.Config.database import get_db_connection



class TokenAuditRepository: 
    
 @staticmethod
 def create(audit_data: TokenAuditCreate) -> Optional[TokenAudit]:
        """Versão com logs detalhados"""
        conn = None
        try:
            print(f"[AUDIT] Tentando registrar: {audit_data.action}")  # Log de debug
            
            conn = get_db_connection()
            cur = conn.cursor()
            
            query = """
                INSERT INTO tokens_audit_log 
                (user_id, token_type, action, token_jti, error, ip_address, user_agent)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                RETURNING id, timestamp
            """
            params = (
                audit_data.user_id,
                audit_data.token_type,
                audit_data.action,
                audit_data.token_jti,
                audit_data.error,
                audit_data.ip_address,
                audit_data.user_agent
            )
            
            cur.execute(query, params)
            result = cur.fetchone()
            conn.commit()
            
            print(f"[AUDIT] Registro criado com ID: {result[0] if result else None}")
            return result
            
        except Exception as e:
            print(f"[AUDIT ERROR] Falha ao registrar: {str(e)}")
            if conn:
                conn.rollback()
            return None
        finally:
            if conn:
                conn.close()
                    
                
 @staticmethod
 def get_by_user(user_id: str, limit: int = 100) -> list[TokenAudit]:
        """Obtém registros de auditoria para um usuário específico"""
        conn = None
        try:
            conn = get_db_connection()
            cur = conn.cursor(cursor_factory=RealDictCursor)
            
            query = """
                SELECT id, timestamp, user_id, token_type, action,
                    token_jti, error, ip_address, user_agent, additional_data
                FROM tokens_audit_log
                WHERE user_id = %s
                ORDER BY timestamp DESC
                LIMIT %s
            """
            
            cur.execute(query, (user_id, limit))
            
            results = []
            for row in cur.fetchall():
                # Converte additional_data de TEXT para dict
                additional_data = None
                if row['additional_data']:
                    try:
                        additional_data = json.loads(row['additional_data'])
                    except json.JSONDecodeError:
                        additional_data = {'raw_data': row['additional_data']}
                
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
                        user_agent=row['user_agent'],
                        additional_data=additional_data
                    )
                )
            
            return results
            
        except psycopg2.Error as e:
            print(f"Database error while fetching audit logs: {e}")
            return []
        finally:
            if conn:
                conn.close()