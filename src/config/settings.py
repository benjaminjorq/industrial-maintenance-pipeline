
import os
import logging
from dotenv import load_dotenv

# Fuerza la lectura del archivo .env en UTF-8 para soportar caracteres
# especiales en credenciales y configuraciones locales.

load_dotenv(encoding="utf-8")

def get_env_variable(var_name: str) -> str:
    """Carga y valida la configuración del pipeline desde variables de entorno."""

    value = os.getenv(var_name)
    
    if not value:
        logging.error("Falla crítica: Variable de entorno '%s' no encontrada.", var_name)
        raise ValueError(f"Falta variable de entorno requerida: {var_name}")
        
    return value


# Base de Datos Origen (PostgreSQL)

DB_HOST = get_env_variable("DB_HOST")
DB_PORT = get_env_variable("DB_PORT")
DB_NAME = get_env_variable("DB_NAME")
DB_USER = get_env_variable("DB_USER")
DB_PASSWORD = get_env_variable("DB_PASSWORD")

# Google Cloud Platform (GCP)

GCP_PROJECT_ID = get_env_variable("GCP_PROJECT_ID")

# Buckets (Data Lake - Medallion Architecture)

GCS_BUCKET_BRONZE = get_env_variable("GCS_BUCKET_BRONZE")
GCS_BUCKET_SILVER = get_env_variable("GCS_BUCKET_SILVER")

# BigQuery (Data Warehouse)

BQ_DATASET_SILVER= get_env_variable("BQ_DATASET_SILVER")
BQ_DATASET_GOLD = get_env_variable("BQ_DATASET_GOLD")

# Conexión Remota SFTP

SFTP_HOST = get_env_variable("SFTP_HOST")
SFTP_PORT = get_env_variable("SFTP_PORT")
SFTP_USER = get_env_variable("SFTP_USER")
SFTP_PASSWORD = get_env_variable("SFTP_PASSWORD")
SFTP_REMOTE_PATH = get_env_variable("SFTP_REMOTE_PATH")