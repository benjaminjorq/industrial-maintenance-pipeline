import logging
from google.cloud import bigquery
from src.config.settings import GCP_PROJECT_ID, GCS_BUCKET_SILVER, BQ_DATASET_SILVER

logger = logging.getLogger(__name__)

def load_parquet_to_bq_silver(table_name: str, ingestion_date: str) -> None:
    """Carga un archivo Parquet desde la capa Silver en GCS hacia BigQuery.

    Transfiere los datos limpios almacenados en Cloud Storage hacia una tabla
    nativa en el Data Warehouse, dejándolos listos para la construcción
    de la capa Gold.

    Args:
        table_name: Nombre de la tabla a cargar.
        ingestion_date: Fecha de partición en formato 'YYYY-MM-DD' para 
            ubicar el archivo en el Data Lake.

    Raises:
        Exception: Si el trabajo de carga de BigQuery falla o es interrumpido.
    """
    logger.info("Iniciando carga a BigQuery Silver para: %s", table_name)
    
    # 1. Nos conectamos a BigQuery

    client = bigquery.Client(project=GCP_PROJECT_ID)
    
    # Construye la ruta del archivo Parquet en Cloud Storage siguiendo
    # la estructura de particionamiento Hive utilizada en la capa Silver.
    # Ejemplo:
    # gs://bucket-silver/plants/ingestion_date=2026-07-28/plants_2026-07-28.parquet

    uri = f"gs://{GCS_BUCKET_SILVER}/{table_name}/ingestion_date={ingestion_date}/{table_name}_{ingestion_date}.parquet"
    
    # Define la tabla destino en BigQuery dentro del dataset Silver.
    # Ejemplo:
    # proyecto.dataset_silver.plants
    # industrial-data-pipeline.industrial_silver.plants

    table_id = f"{GCP_PROJECT_ID}.{BQ_DATASET_SILVER}.{table_name}"
    
    # Configura el comportamiento del proceso de carga.
    # Actualmente se utiliza WRITE_TRUNCATE para reemplazar completamente
    # la tabla destino en cada ejecución.
    # En una implementación incremental podría reemplazarse por WRITE_APPEND
    # o una estrategia basada en MERGE.

    job_config = bigquery.LoadJobConfig(
        source_format=bigquery.SourceFormat.PARQUET,
        # Truncamos la tabla para probar
        write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE,
    )
    
    try:
        # Ejecuta el job de carga desde Cloud Storage hacia BigQuery.
        logger.info("Cargando archivo: %s", uri)
        load_job = client.load_table_from_uri(uri, table_id, job_config=job_config)
        
        # Espera la finalización del job antes de continuar,
        # asegurando que la tabla esté disponible para las siguientes etapas.
        load_job.result() 
        
        # Obtiene información de la tabla cargada para registrar métricas básicas.
        destination_table = client.get_table(table_id)
        logger.info("Carga exitosa. La tabla %s ahora tiene %s filas.", table_name, destination_table.num_rows)
        
    except Exception as e:
        logger.error("Error cargando la tabla %s en BigQuery: %s", table_name, e)
        raise