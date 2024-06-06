class Config:
    JWT_TOKEN_LOCATION = ["query_string"]
    JWT_ALGORITHM = "HS256"
    JWT_SECRET_KEY = ""
    SECRET_KEY = ""
    API_KEY = ""
    UPLOAD_FOLDER = "/app/static/storage"
    SQLALCHEMY_DATABASE_URI = "mariadb+pymysql://USER:PASS@HOST/BASE?charset=utf8mb4"
    SQLALCHEMY_ECHO = True
    SQLALCHEMY_POOL_SIZE = 10
    SQLALCHEMY_POOL_TIMEOUT = 30
    SQLALCHEMY_POOL_RECYCLE = 1800
    SQLALCHEMY_MAX_OVERFLOW = 5
    SQLALCHEMY_ENGINE_OPTIONS = {"pool_pre_ping": True}
