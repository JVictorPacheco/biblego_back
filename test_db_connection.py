from app.Utils.database_connection import DatabaseConnection

db_config = {
    "dbname": "BiblieGo",
    "user": "postgres",
    "password": "Akira!4321",
    "host": "localhost",
    "port": "5432"
}

def test_db_connection():
    db = DatabaseConnection(**db_config)

   # print(db)

    try:
        db.connect()
        query = "SELECT Count(verse) from Verses;"
        result = db.execute_query(query)

        if result:
            print("Conexão bem-sucedida! Resultado da query:")
            print(result)
        else:
            print("Erro ao executar a query.")

    except Exception as e:
        print(f"Erro durante a conexão ou execução da query: {e}")

    finally:
        db.close()

# Mova o bloco if __name__ == "__main__": para fora da função
if __name__ == "__main__":
    test_db_connection()
