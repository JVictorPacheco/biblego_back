import psycopg2
from psycopg2 import pool
from flask import current_app

class AuditDatabase:
    _connection_pool = None

    @classmethod
    def initialize(cls):
        cls._connection_pool = psycopg2.pool.SimpleConnectionPool(
            minconn=1,
            maxconn=5,
            dbname="biblego",
            user="biblego",
            password="biblego%123!",
            host="177.70.98.148",
            port="6543"
        )

    @classmethod
    def get_connection(cls):
        if cls._connection_pool is None:
            cls.initialize()
        return cls._connection_pool.getconn()

    @classmethod
    def release_connection(cls, connection):
        if cls._connection_pool is not None:
            cls._connection_pool.putconn(connection)

# Inicializa quando o módulo é carregado
AuditDatabase.initialize()