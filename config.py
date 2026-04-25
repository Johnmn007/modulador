import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev_secret_key_12345")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # Carpeta para archivos subidos y reportes
    UPLOAD_FOLDER = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'app/static/uploads')
    REPORTS_FOLDER = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'app/static/reports')

class DevelopmentConfig(Config):
    DEBUG = True
    # Fallback a SQLite si no se configuran variables de MySQL
    if os.getenv('DB_NAME'):
        SQLALCHEMY_DATABASE_URI = (
            f"mysql+pymysql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}"
            f"@{os.getenv('DB_HOST', 'localhost')}:{os.getenv('DB_PORT', '3306')}/{os.getenv('DB_NAME')}"
        )
    else:
        SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(os.path.abspath(os.path.dirname(__file__)), 'app_dev.db')

class ProductionConfig(Config):
    DEBUG = False
    # En producción es obligatorio usar la URL completa o variables definidas
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL') or (
        f"mysql+pymysql://{os.getenv('PROD_DB_USER')}:{os.getenv('PROD_DB_PASSWORD')}"
        f"@{os.getenv('PROD_DB_HOST')}:{os.getenv('PROD_DB_PORT', '3306')}/{os.getenv('PROD_DB_NAME')}"
    )

class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.getenv("TEST_DATABASE_URL", "sqlite:///:memory:")

config_by_name = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "testing": TestingConfig,
    "default": DevelopmentConfig
}