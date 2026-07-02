import os
import secrets
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", secrets.token_hex(32))
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'app/static/uploads')
    REPORTS_FOLDER = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'app/static/reports')

class DevelopmentConfig(Config):
    DEBUG = True
    # Fallback a SQLite si no se configuran variables de MySQL
    if os.getenv('DB_NAME'):
        SQLALCHEMY_DATABASE_URI = (
            f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}"
            f"@{os.getenv('DB_HOST', 'localhost')}:{os.getenv('DB_PORT', '5432')}/{os.getenv('DB_NAME')}"
        )
    else:
        SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(os.path.abspath(os.path.dirname(__file__)), 'app_dev.db')

class ProductionConfig(Config):
    DEBUG = False
    SECRET_KEY = os.getenv("PROD_SECRET_KEY") or os.getenv("SECRET_KEY") or secrets.token_hex(32)
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL') or (
        f"postgresql://{os.getenv('PROD_DB_USER')}:{os.getenv('PROD_DB_PASSWORD')}"
        f"@{os.getenv('PROD_DB_HOST')}:{os.getenv('PROD_DB_PORT', '5432')}/{os.getenv('PROD_DB_NAME')}"
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