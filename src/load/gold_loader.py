import logging
from pathlib import Path
from google.cloud import bigquery

from src.config.settings import GCP_PROJECT_ID

logger = logging.getLogger(__name__)

# Módulo: Gold Loader
# Ejecuta modelos SQL analíticos de la capa Gold en BigQuery.
# Mantiene separada la lógica de negocio (SQL) de la lógica de ejecución (Python).
# Cada archivo SQL representa un modelo independiente del pipeline.

def execute_gold_layer(sql_folder: Path) -> None:
    """Ejecuta los modelos analíticos de la capa Gold en BigQuery.

    Lee los archivos SQL almacenados en el directorio indicado y ejecuta
    cada transformación dentro del Data Warehouse. La lógica de negocio,
    tabla destino y estrategia de materialización quedan definidas dentro
    de cada modelo SQL.

    Args:
        sql_folder: Ruta al directorio que contiene los modelos SQL de la capa Gold.

    Raises:
        Exception: Si falla la ejecución de un modelo en BigQuery, deteniendo
            el pipeline para evitar la generación de datos analíticos inconsistentes.
    """
    logger.info("Iniciando construcción de la Capa Gold (Modelos Analíticos)")
    
    client = bigquery.Client(project=GCP_PROJECT_ID)
    
    if not sql_folder.exists():
        logger.error("Fallo crítico: El directorio de modelos Gold '%s' no existe.", sql_folder)
        return
        
    # Ordena los modelos para ejecución
    # (ejemplo: 01_tabla_base.sql, 02_tabla_metricas.sql).
    sql_files = sorted(sql_folder.glob("*.sql"))
    
    if not sql_files:
        logger.warning("No se encontraron modelos SQL en %s", sql_folder)
        return

    logger.info("Se detectaron %s modelos Gold para procesar.", len(sql_files))

    for sql_file in sql_files:
        model_name = sql_file.stem
        
        with open(sql_file, "r", encoding="utf-8") as file:
            sql_query = file.read().strip()
            
        # Evita ejecutar archivos vacíos que podrían generar errores
        # durante el procesamiento del job en BigQuery.

        if not sql_query:
            logger.warning("El archivo '%s' está vacío. Omitiendo ejecución...", sql_file.name)
            continue
            
        logger.info("Ejecutando modelo Gold: '%s'", model_name)
        
        try:
            query_job = client.query(sql_query)
            # Espera la finalización del job antes de ejecutar el siguiente modelo.
            query_job.result()
            logger.info("Modelo '%s' construido exitosamente.", model_name)
            
        except Exception as error:
            logger.error("Error construyendo el modelo '%s': %s", model_name, error, exc_info=True)
            raise
            
    logger.info("Procesamiento de la Capa Gold finalizado correctamente.")