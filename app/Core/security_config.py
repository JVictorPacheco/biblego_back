
class SecurityConfig:

    SECRET_KEY = "pythonjwt"  # Em produção, use variáveis de ambiente
    ALGORITHM = "HS256"
    TOKEN_EXPIRE_HOURS = 2