import json
import logging
from datetime import datetime, timezone
from pathlib import Path
import pandas as pd

from src.database.connection import get_db_connection
from src.config.settings import GCS_BUCKET_BRONZE
from utils.gcs_uploader import upload_file

logger = logging.getLogger(__name__)

def extract_table(query):
    """Ejecuta una consulta SQL en PostgreSQL y devuelve un DataFrame."""

    logger.info("Conectando a PostgreSQL para extraer datos")
    conn = get_db_connection()
    
    try:
        df = pd.read_sql_query(query, conn)
        logger.info("Filas recuperadas: %s", len(df))
    finally:
        conn.close()
        
    return df

def save_csv(df, output_dir, filename):
    """Guarda un DataFrame como CSV."""
    output_dir.mkdir(parents=True, exist_ok=True)
    csv_path = output_dir / filename
    
    logger.info("Guardando CSV local en: %s", csv_path)
    df.to_csv(csv_path, index=False, encoding="utf-8")
    
    return csv_path

def save_metadata(table_name: str, csv_path: Path, row_count: int, generated_at: datetime, query_file: str) -> Path:
    """Genera un archivo JSON con la información de auditoría de la extracción.

    Args:
        table_name: Nombre de la tabla extraída.
        csv_path: Ruta del archivo CSV generado.
        row_count: Número de registros extraídos.
        generated_at: Fecha y hora de la extracción.
        query_file: Archivo SQL utilizado.

    Returns:
        Ruta del archivo de metadatos generado.
    """

    metadata = {
        "source": "postgresql",
        "table": table_name,
        "file_name": csv_path.name,
        "rows": row_count,
        "file_size_bytes": csv_path.stat().st_size,
        "generated_at": generated_at.isoformat(),
        "query_file": query_file,
    }
    
    metadata_path = csv_path.parent / "metadata.json"
    
    with open(metadata_path, "w", encoding="utf-8") as file:
        json.dump(metadata, file, indent=4)
        
    return metadata_path

def run(table_name: str, query: str, bronze_path: Path, ingestion_date: str, query_file: str = "unknown") -> None:
    """Ejecuta el proceso completo de extracción de una tabla hacia Bronze.

    El proceso incluye:
    - Extracción desde PostgreSQL;
    - Almacenamiento local del CSV;
    - Generación de metadatos de auditoría;
    - Respaldo de ambos archivos en Cloud Storage.

    Args:
        table_name: Nombre de la tabla a procesar.
        query: Consulta SQL de extracción.
        bronze_path: Directorio raíz de la capa Bronze.
        ingestion_date: Fecha de partición utilizada en el almacenamiento.
        query_file: Nombre del archivo SQL utilizado.

    Raises:
        RuntimeError: Si falla la carga de archivos a Cloud Storage.
        Exception: Propaga cualquier error ocurrido durante la extracción.
    """

    logger.info("Iniciando proceso de extracción Bronze para la tabla: '%s'", table_name)
    now = datetime.now(timezone.utc)
    
    output_dir = bronze_path / table_name / f"ingestion_date={ingestion_date}"
    filename = f"{table_name}_{ingestion_date}.csv"
    cloud_folder = f"{table_name}/ingestion_date={ingestion_date}"

    try:
        df = extract_table(query)

        # Evita generar archivos vacíos y consumir almacenamiento innecesariamente.
        if df.empty:
            logger.warning("La tabla '%s' está vacía. Se omite la creación de archivos.", table_name)
            return
            
        csv_path = save_csv(df, output_dir, filename)
        metadata_path = save_metadata(table_name, csv_path, len(df), now, query_file)
        
        logger.info("Respaldando archivos en Cloud Storage (Bronze)")
        
        upload_csv_ok = upload_file(csv_path, GCS_BUCKET_BRONZE, f"{cloud_folder}/{csv_path.name}")
        upload_meta_ok = upload_file(metadata_path, GCS_BUCKET_BRONZE, f"{cloud_folder}/{metadata_path.name}")
        
        if not upload_csv_ok or not upload_meta_ok:
            raise RuntimeError("Fallo crítico: GCS Uploader retornó False. No se pudo respaldar en la nube.")
        
        logger.info("Proceso exitoso y respaldado en la nube para: '%s'\n", table_name)
        
    except Exception as error:
        logger.error("Error crítico procesando la tabla '%s': %s", table_name, error, exc_info=True)
        raise