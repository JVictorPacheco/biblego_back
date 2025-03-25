import sys
import os

# Adiciona o diretório raiz ao PYTHONPATH
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))


import psycopg2

class DatabaseConnection:
    #Inicializa os parâmetros de conexão
    def __init__(self, dbname, user, password, host, port):
        self.connection_parameters = {
            "dbname": dbname,
            "user": user,
            "password": password,
            "host": host,
            "port": port
        }
        self.connection = None
        self.cursor = None

    #Estabelece a conexão com o banco de dados.
    def connect(self):
        try:
            self.connection = psycopg2.connect(**self.connection_parameters)
            self.cursor = self.connection.cursor()
            print("Conexão bem sucedida")
        except Exception as e:
            print(f"Erro ao conectar no bando de dados: {e}")
            raise

    # executa uma consulta SQL e retorna os resultados.
    def execute_query(self, query, params=None):
        if not self.cursor:
            print("Cursor não está disponível. Verifique a conexão com o banco de dados.")
            return None
        
        try:
            self.cursor.execute(query, params or ())
            return self.cursor.fetchall()
        except Exception as e:
            print(f"Erro ao executar a query: {e}")
            return None
        
    def commit(self):
        """
        Confirma as alterações no banco de dados.
        """
        if self.connection:
            self.connection.commit()


    def close(self):
        """
        Fecha a conexão com o banco de dados.
        """
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()
            print("conexão fechada")       

