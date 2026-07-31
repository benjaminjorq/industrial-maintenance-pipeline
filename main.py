import logging
from datetime import datetime, timezone
from pathlib import Path

from src.extractors import postgres_extractor
from src.transform import transformer
from src.load.bigquery_loader import load_parquet_to_bq_silver
from src.load.gold_loader import execute_gold_layer

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger(__name__)

# Definición de rutas del proyecto

BASE_DIR = Path(__file__).parent
SQL_DIR = BASE_DIR / "sql"
BRONZE_DIR = BASE_DIR / "data" / "bronze"
SILVER_DIR = BASE_DIR / "data" / "silver"
GOLD_DIR = SQL_DIR / "gold"

def main(target_date: str = None, target_tables: list = None) -> None:
    """Orquesta la ejecución end-to-end del pipeline de datos.

    Gestiona la extracción desde fuentes internas, transformación hacia la capa
    Silver, carga a BigQuery y construcción de modelos analíticos en la capa Gold.

    Args:
        target_date: Fecha de la partición (YYYY-MM-DD). 
        target_tables: Lista de tablas específicas a procesar.
    """
    
    run_date = target_date if target_date else datetime.now(timezone.utc).strftime("%Y-%m-%d")
    logger.info("Iniciando pipeline de datos para la partición: %s", run_date)
    
    # Fase 1: Extracción, Transformación y Carga (Tablas Internas - Base de Datos)
    
    if not SQL_DIR.exists():
        logger.error("Fallo crítico: El directorio %s no existe.", SQL_DIR)
        return
        
    sql_files = list(SQL_DIR.glob("*.sql"))
    logger.info("Se detectaron %s tablas internas para procesar.", len(sql_files))
    
    for sql_file in sql_files:
        table_name = sql_file.stem
        file_name = sql_file.name
        
        if table_name.startswith("gold_"):
            continue
        
        # Filtro de ejecución manual para reprocesar tablas específicas
        
        if target_tables and table_name not in target_tables:
            logger.info("Omitiendo tabla interna '%s' por configuración manual.", table_name)
            continue
        
        try:
            with open(sql_file, "r", encoding="utf-8") as file:
                query = file.read()
            
            # Paso A: Extracción desde Postgres a CSV (Capa Bronze)

            postgres_extractor.run(
                table_name=table_name,
                query=query,
                bronze_path=BRONZE_DIR,
                ingestion_date=run_date,
                query_file=file_name
            )
            
            # Paso B: Limpieza a formato Parquet (Capa Silver Local)

            transformer.run(
                table_name=table_name,
                bronze_path=BRONZE_DIR,
                silver_path=SILVER_DIR,
                ingestion_date=run_date
            )
            
            # Paso C: Carga del archivo Parquet hacia BigQuery

            logger.info("Cargando tabla interna '%s' a BigQuery Silver", table_name)
            load_parquet_to_bq_silver(
                table_name=table_name,
                ingestion_date=run_date
            )
            
        except Exception as error:
            logger.error("Error procesando tabla '%s'.", table_name, exc_info=True)
            continue
            
    # Fase 2: Procesamiento y Carga de Tablas Externas
    # Archivos que no vienen de la BD (ej. Conexión Externa (SFTP)). 
    
    external_tables = []
    
    for ext_table in external_tables:
        if target_tables and ext_table not in target_tables:
            logger.info("Omitiendo tabla externa '%s' por configuración manual.", ext_table)
            continue
            
        try:
            logger.info("Procesando tabla externa '%s'", ext_table)
            
            # Limpieza del archivo raw a Parquet
            transformer.run(
                table_name=ext_table,
                bronze_path=BRONZE_DIR,
                silver_path=SILVER_DIR,
                ingestion_date=run_date
            )
            
            # Carga hacia BigQuery
            logger.info("Cargando tabla externa '%s' a BigQuery Silver...", ext_table)
            load_parquet_to_bq_silver(
                table_name=ext_table,
                ingestion_date=run_date
            )
            
        except Exception as error:
            logger.error("Error procesando tabla externa '%s'.", ext_table, exc_info=True)
            continue

    # Fase 3: Procesamiento de la Capa Gold (Modelos Gerenciales)

    logger.info("Iniciando construcción de la capa Gold")
    try:
        execute_gold_layer(GOLD_DIR)
    except Exception:
        logger.error("Fallo crítico durante la construcción de la capa Gold.", exc_info=True)
        raise

    logger.info("Pipeline End-to-End finalizado correctamente.")

if __name__ == "__main__":
    main()