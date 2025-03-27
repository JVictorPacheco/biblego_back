from app.Utils.database_connection import DatabaseConnection

# Configuração do banco de dados
DB_CONFIG = {
    "dbname": "biblego",
    "user": "biblego",
    "password": "biblego%123!",
    "host": "177.70.98.148",
    "port": "6543"
    }


def get_db_connection():
    db = DatabaseConnection(**DB_CONFIG)
    db.connect()
    return db
