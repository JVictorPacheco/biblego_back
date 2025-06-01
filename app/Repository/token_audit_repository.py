from typing import List, Optional, Dict, Any
from app.Models.token_audit import TokenAudit, TokenAuditCreate
import json
import psycopg2
from psycopg2.extras import RealDictCursor
from app.Config.database import get_db_connection



class TokenAuditRepository: 
    @staticmethod
    def create(audit_data: TokenAuditCreate) -> Optional[TokenAudit]:
        """Persiste um registro de auditoria no banco de dados"""
        conn = None
        try:
            conn = get_db_connection()
            cur = conn.cursor(cursor_factory=RealDictCursor)
            
            # Prepara os dados para o banco
            db_data = {
                'user_id': audit_data.user_id,
                'token_type': audit_data.token_type.value,
                'action': audit_data.action.value,
                'token_jti': audit_data.token_jti,
                'error': audit_data.error,
                'ip_address': audit_data.ip_address,
                'user_agent': audit_data.user_agent,
                'additional_data': json.dumps(audit_data.additional_data) 
                                 if audit_data.additional_data else None
            }
            
            # Remove valores None
            db_data = {k: v for k, v in db_data.items() if v is not None}
            
            # Construção dinâmica da query
            columns = ', '.join(db_data.keys())
            placeholders = ', '.join(['%s'] * len(db_data))
            query = f"""
                INSERT INTO tokens_audit_log ({columns})
                VALUES ({placeholders})
                RETURNING id, timestamp
            """
            
            cur.execute(query, list(db_data.values()))
            result = cur.fetchone()
            conn.commit()
            
            if result:
                return TokenAudit(
                    id=result['id'],
                    timestamp=result['timestamp'],
                    **audit_data.dict()
                )
            return None
            
        except psycopg2.Error as e:
            print(f"Database error during audit: {e}")
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