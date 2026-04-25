# app/services/logger.py
import logging
import os
from datetime import datetime
from logging.handlers import RotatingFileHandler

# Crear directorio de logs si no existe
log_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'logs')
os.makedirs(log_dir, exist_ok=True)

# Configurar formato de log
log_format = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

def setup_logger(name, log_file=None, level=logging.INFO):
    """Configura y retorna un logger"""
    
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Evitar duplicación de handlers
    if logger.handlers:
        return logger
    
    # Handler para archivo (rotativo)
    if log_file:
        file_handler = RotatingFileHandler(
            os.path.join(log_dir, log_file),
            maxBytes=10485760,  # 10MB
            backupCount=5,
            encoding='utf-8'
        )
        file_handler.setFormatter(log_format)
        logger.addHandler(file_handler)
    
    # Handler para consola
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(log_format)
    logger.addHandler(console_handler)
    
    return logger

# Loggers específicos del sistema
app_logger = setup_logger('app', 'app.log')
db_logger = setup_logger('database', 'database.log')
auth_logger = setup_logger('auth', 'auth.log')
riesgo_logger = setup_logger('riesgo', 'riesgo.log')
importacion_logger = setup_logger('importacion', 'importacion.log')

def log_exception(logger, e, context=""):
    """Registra una excepción con contexto"""
    logger.error(f"Excepción en {context}: {str(e)}", exc_info=True)