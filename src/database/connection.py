import logging
import psycopg2
from tenacity import (retry, retry_if_exception_type, stop_after_attempt, wait_exponential, before_sleep_log)
from src.config.settings import DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD

logger = logging.getLogger(__name__)

@retry(
    retry=retry_if_exception_type((psycopg2.OperationalError, psycopg2.InterfaceError)),
    wait=wait_exponential(multiplier=2, min=2, max=10),
    stop=stop_after_attempt(3),
    before_sleep=before_sleep_log(logger, logging.WARNING),
    reraise=True
)
def get_db_connection():
    """Crea y retorna una conexión a la base de datos PostgreSQL.

    Returns:
        psycopg2.extensions.connection: Conexión activa a PostgreSQL.

    Raises:
        psycopg2.Error: Si ocurre un error al establecer la conexión.
    """
    logger.info("Intentando conectar a PostgreSQL")

    connection = psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        connect_timeout=10,
    )

    logger.info("Conexión a PostgreSQL establecida")
    return connection