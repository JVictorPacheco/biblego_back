
class SecurityConfig:

    SECRET_KEY = "pythonjwt"  # EM PRODUÇÃO: os.getenv("JWT_SECRET_KEY")
    ALGORITHM = "HS256"
    #TOKEN_EXPIRE_MINUTES = 1
    TOKEN_EXPIRE_HOURS = 1/60
    REFRESH_TOKEN_EXPIRE_DAYS = 30