"""Módulo de configuración central del pipeline.

Centraliza la carga y validación de las variables de entorno requeridas por
el pipeline. Aplica un enfoque *fail-fast*, deteniendo la ejecución durante
la importación del módulo si falta alguna configuración obligatoria.
"""

import os
import logging
from dotenv import load_dotenv

# Fuerza la lectura del archivo .env en UTF-8 para soportar caracteres
# especiales en credenciales y configuraciones locales.

load_dotenv(encoding="utf-8")

def get_env_variable(var_name: str) -> str:
    """Obtiene y valida una variable de entorno obligatoria.

    Recupera el valor asociado a una variable de entorno y verifica que esté
    definida. Si la variable no existe o está vacía, lanza una excepción para
    impedir que el pipeline continúe con una configuración incompleta.

    Args:
        var_name: Nombre de la variable de entorno.

    Returns:
        Valor asociado a la variable de entorno.

    Raises:
        ValueError: Si la variable no está definida o su valor es vacío.
    """
    value = os.getenv(var_name)
    
    if not value:
        logging.error("Falla crítica: Variable de entorno '%s' no encontrada.", var_name)
        raise ValueError(f"Falta variable de entorno requerida: {var_name}")
        
    return value

# Instrucciones de mantenimiento: 
# Si agregas una nueva variable en el archivo .env (ej. credenciales de una nueva API), 
# debes registrarla aquí creando una nueva constante.


# Base de Datos Origen (PostgreSQL Local)

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
