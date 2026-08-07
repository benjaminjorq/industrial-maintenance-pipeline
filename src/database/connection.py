import logging
import psycopg2
from src.config.settings import DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD

logger = logging.getLogger(__name__)

def get_db_connection():
    """Crea y retorna una conexión a la base de datos PostgreSQL.

    Returns:
        psycopg2.extensions.connection: Conexión activa a PostgreSQL.

    Raises:
        psycopg2.Error: Si ocurre un error al establecer la conexión.
    """
    try:
        logger.info("Intentando Conectar a PostgreSQL")
        
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )
        
        return conn
        
    except psycopg2.Error as error:
        logger.error("Error crítico al conectar a PostgreSQL: %s", error)
        raise