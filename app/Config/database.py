from app.Utils.database_connection import DatabaseConnection

# Configuração do banco de dados
DB_CONFIG = {
    "dbname": "biblego",
    "user": "postgres",
    "password": "Akira.321",
    "host": "localhost",
    "port": "5432"
    }


def get_db_connection():
    db = DatabaseConnection(**DB_CONFIG)
    db.connect()
    return db
