import os
from app.Utils.database_connection import DatabaseConnection

def get_db_config():
    """
    Retorna configuração do banco de dados baseada em variáveis de ambiente.
    Para desenvolvimento local, usa valores padrão se variáveis não estiverem definidas.
    """
    return {
        "dbname": os.getenv("DATABASE_NAME", "biblego"),
        "user": os.getenv("DATABASE_USER", "biblego"), 
        "password": os.getenv("DATABASE_PASSWORD", "biblego%123!"),
        "host": os.getenv("DATABASE_HOST", "177.70.98.148"),
        "port": os.getenv("DATABASE_PORT", "6543")
    }

def get_db_connection():
    """
    Cria conexão com banco usando configurações de ambiente
    """
    db_config = get_db_config()
    db = DatabaseConnection(**db_config)
    db.connect()
    return db