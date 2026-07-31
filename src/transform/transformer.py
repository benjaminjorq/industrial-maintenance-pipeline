import logging
from pathlib import Path
from datetime import datetime, timezone
import pandas as pd

from src.config.settings import GCS_BUCKET_SILVER
from utils.gcs_uploader import upload_file
from src.transform.data_cleaning_functions import (clean_spaces, convert_to_uppercase, convert_to_lowercase,
convert_to_title_case, fix_negative_numbers, invalidate_zero_costs, set_missing_dates_to_null, fix_inverted_dates)

logger = logging.getLogger(__name__)

# Instrucciones de mantenimiento para las Reglas de Negocio:
# 1. Si necesitas limpiar una columna nueva en una tabla existente, busca la función 'apply_[tabla]_rules' 
#    y agrega el llamado a la herramienta de limpieza correspondiente.
# 2. Si necesitas limpiar una tabla completamente nueva, crea una nueva función 'apply_nueva_tabla_rules'
#    y luego regístrala dentro de 'BUSINESS_RULES_MAP' usando el nombre exacto de la tabla.

def apply_plants_rules(df: pd.DataFrame) -> pd.DataFrame:
    df = clean_spaces(df, "plant_name")
    df = clean_spaces(df, "region")
    return convert_to_title_case(df, "region")

def apply_product_categories_rules(df: pd.DataFrame) -> pd.DataFrame:
    df = clean_spaces(df, "category_name")
    return convert_to_title_case(df, "category_name")

def apply_suppliers_rules(df: pd.DataFrame) -> pd.DataFrame:
    df = clean_spaces(df, "supplier_name")
    df = clean_spaces(df, "country")
    return convert_to_title_case(df, "country")

def apply_machines_rules(df: pd.DataFrame) -> pd.DataFrame:
    return convert_to_uppercase(df, "status")

def apply_raw_materials_rules(df: pd.DataFrame) -> pd.DataFrame:
    df = clean_spaces(df, "unit_of_measure")
    return convert_to_lowercase(df, "unit_of_measure")

def apply_products_rules(df: pd.DataFrame) -> pd.DataFrame:
    df = fix_negative_numbers(df, "standard_cost")
    return invalidate_zero_costs(df, "standard_cost")

def apply_production_orders_rules(df: pd.DataFrame) -> pd.DataFrame:
    df = convert_to_uppercase(df, "status")
    return set_missing_dates_to_null(df, "actual_start_date")

def apply_production_yields_rules(df: pd.DataFrame) -> pd.DataFrame:
    return fix_negative_numbers(df, "scrap_quantity")

def apply_downtime_events_rules(df: pd.DataFrame) -> pd.DataFrame:
    return fix_inverted_dates(df, "start_timestamp", "end_timestamp")

# Diccionario de enrutamiento que conecta cada tabla con sus respectivas reglas de limpieza.

BUSINESS_RULES_MAP = {
    "plants": apply_plants_rules,
    "product_categories": apply_product_categories_rules,
    "suppliers": apply_suppliers_rules,
    "machines": apply_machines_rules,
    "raw_materials": apply_raw_materials_rules,
    "products": apply_products_rules,
    "production_orders": apply_production_orders_rules,
    "production_yields": apply_production_yields_rules,
    "downtime_events": apply_downtime_events_rules
}

def clean_data(df: pd.DataFrame, table_name: str) -> pd.DataFrame:
    """Normaliza nombres de columnas y aplica transformaciones específicas por tabla.

    Ejecuta las reglas definidas en BUSINESS_RULES_MAP según la tabla recibida
    y agrega registro de ingesta antes de almacenar los datos en la capa Silver.

    Args:
        df: DataFrame con los datos provenientes de la capa Bronze.
        table_name: Nombre de la tabla sobre la cual se aplicarán las transformaciones.

    Returns:
        DataFrame transformado listo para ser almacenado en formato Silver.
    """
    logger.info("Iniciando limpieza de datos para la tabla: %s", table_name)
    
    df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")
    
    if table_name in BUSINESS_RULES_MAP:
        logger.info("Aplicando reglas de limpieza específicas para la tabla '%s'", table_name)
        df = BUSINESS_RULES_MAP[table_name](df)
    else:
        logger.info("La tabla '%s' no requiere reglas de limpieza adicionales.", table_name)
        
    df["ingested_at"] = datetime.now(timezone.utc)
    
    logger.info("Limpieza finalizada. Columnas resultantes: %s", list(df.columns))
    return df

def save_parquet(df: pd.DataFrame, output_dir: Path, filename: str) -> Path:
    """Convierte un DataFrame a formato Parquet y lo almacena localmente.

    Crea el directorio destino si no existe y guarda el dataset transformado
    utilizando formato columnar optimizado para procesamiento analítico.

    Args:
        df: DataFrame procesado de la capa Silver.
        output_dir: Directorio local donde se almacenará el archivo.
        filename: Nombre del archivo Parquet generado.

    Returns:
        Ruta completa del archivo Parquet generado.
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    parquet_path = output_dir / filename
    
    logger.info("Guardando archivo Parquet optimizado en: %s", parquet_path)
    df.to_parquet(parquet_path, index=False, engine="pyarrow")
    
    return parquet_path

def run(table_name: str, bronze_path: Path, silver_path: Path, ingestion_date: str) -> None:
    """Ejecuta el flujo de transformación desde Bronze hacia Silver.

    Lee los archivos CSV provenientes de la capa Bronze, aplica reglas de
    transformación, genera un archivo Parquet y lo carga en Cloud Storage.

    Args:
        table_name: Nombre de la tabla a procesar.
        bronze_path: Ruta base de los datos Bronze.
        silver_path: Ruta local donde se almacenan temporalmente los archivos Parquet.
        ingestion_date: Fecha de partición del proceso en formato YYYY-MM-DD.

    Raises:
        Exception: Si ocurre un error durante la transformación o carga a GCS.
    """
    logger.info("Iniciando transformación Silver para la tabla: '%s'", table_name)
    
    input_dir = bronze_path / table_name / f"ingestion_date={ingestion_date}"
    csv_file = input_dir / f"{table_name}_{ingestion_date}.csv"
    output_dir = silver_path / table_name / f"ingestion_date={ingestion_date}"
    filename = f"{table_name}_{ingestion_date}.parquet"
    cloud_folder = f"{table_name}/ingestion_date={ingestion_date}"
    
    try:
        if not csv_file.exists():
            logger.warning("Archivo crudo no encontrado en: %s. Se omite la transformación.", csv_file)
            return
            
        df_raw = pd.read_csv(csv_file)
        df_clean = clean_data(df_raw, table_name)
        
        parquet_path = save_parquet(df_clean, output_dir, filename)
        
        logger.info("Subiendo Data a Cloud Storage (Bucket Silver)")
        
        if not upload_file(parquet_path, GCS_BUCKET_SILVER, f"{cloud_folder}/{parquet_path.name}"):
            raise RuntimeError("Fallo crítico: GCS Uploader retornó False. No se pudo subir el Parquet.")
        
        logger.info("Transformación y respaldo en nube finalizados exitosamente para: '%s'\n", table_name)
        
    except Exception as error:
        logger.error("Error crítico transformando la tabla '%s': %s", table_name, error, exc_info=True)
        raise