class Config:
    JWT_TOKEN_LOCATION = ["query_string"]
    JWT_ALGORITHM = 'HS256'
    JWT_SECRET_KEY = 'pprfnktechsekta2024'
    SECRET_KEY = 'pprfnktechsekta2024'
    API_KEY = 'pprfkebetvsehrot2024'
    UPLOAD_FOLDER = '/app/static/storage'
    SQLALCHEMY_DATABASE_URI = 'mariadb+pymysql://sysop:0Z3tcFg7FE60YBpKdquwrQRk@pprfnkdb-primary.mariadb.svc.pprfnk.local/cyber?charset=utf8mb4'
    SQLALCHEMY_ECHO = True
    SQLALCHEMY_POOL_SIZE = 10
    SQLALCHEMY_POOL_TIMEOUT = 30
    SQLALCHEMY_POOL_RECYCLE = 1800
    SQLALCHEMY_MAX_OVERFLOW = 5
    SQLALCHEMY_ENGINE_OPTIONS = {'pool_pre_ping': True}
