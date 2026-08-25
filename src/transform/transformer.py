import logging
from pathlib import Path
from datetime import datetime, timezone
import pandas as pd

from src.config.settings import GCS_BUCKET_SILVER
from utils.gcs_uploader import upload_file
from src.transform.data_cleaning_functions import (clean_spaces, convert_to_uppercase, convert_to_lowercase,
convert_to_title_case, fix_negative_numbers, invalidate_zero_costs, set_missing_dates_to_null, fix_inverted_dates)

from src.validations.data_quality import (validate_non_empty, validate_schema, validate_not_null,
validate_unique, validate_accepted_values, validate_positive_values,validate_chronological_order)

logger = logging.getLogger(__name__)

# Reglas de Limpieza por Tabla

def clean_plants_table(df):
    df = clean_spaces(df, "plant_name")
    df = clean_spaces(df, "region")
    return convert_to_title_case(df, "region")

def clean_product_categories_table(df):
    df = clean_spaces(df, "category_name")
    return convert_to_title_case(df, "category_name")

def clean_suppliers_table(df):
    df = clean_spaces(df, "supplier_name")
    df = clean_spaces(df, "country")
    return convert_to_title_case(df, "country")

def clean_quality_control_table(df):
    df = clean_spaces(df, "inspector_name")
    df = convert_to_title_case(df, "inspector_name")
    return fix_negative_numbers(df, "quality_score")

def clean_machines_table(df):
    return convert_to_uppercase(df, "status")

def clean_raw_materials_table(df):
    df = clean_spaces(df, "unit_of_measure")
    return convert_to_lowercase(df, "unit_of_measure")

def clean_products_table(df):
    df = fix_negative_numbers(df, "standard_cost")
    return invalidate_zero_costs(df, "standard_cost")

def clean_production_orders_table(df):
    df = convert_to_uppercase(df, "status")
    return set_missing_dates_to_null(df, "actual_start_date")

def clean_production_yields_table(df):
    return fix_negative_numbers(df, "scrap_quantity")

def clean_downtime_events_table(df):
    return fix_inverted_dates(df, "start_timestamp", "end_timestamp")



CLEANING_RULES = {
    "plants": clean_plants_table,
    "product_categories": clean_product_categories_table,
    "suppliers": clean_suppliers_table,
    "machines": clean_machines_table,
    "raw_materials": clean_raw_materials_table,
    "products": clean_products_table,
    "production_orders": clean_production_orders_table,
    "production_yields": clean_production_yields_table,
    "downtime_events": clean_downtime_events_table,
    "quality_control": clean_quality_control_table
}

# Reglas de Calidad por Tabla

def validate_plants_table(df):
    df = validate_schema(df, "plants", ["plant_id", "plant_name", "region", "is_active"])
    df = validate_not_null(df, "plants", "plant_id")
    df = validate_unique(df, "plants", "plant_id")
    return df

def validate_product_categories_table(df):
    df = validate_schema(df, "product_categories", ["category_id", "category_name"])
    df = validate_not_null(df, "product_categories", "category_id")
    df = validate_unique(df, "product_categories", "category_id")
    return df

def validate_suppliers_table(df):
    df = validate_schema(df, "suppliers", ["supplier_id", "supplier_name", "country"])
    df = validate_not_null(df, "suppliers", "supplier_id")
    df = validate_unique(df, "suppliers", "supplier_id")
    return df

def validate_machines_table(df):
    df = validate_schema(df, "machines", ["machine_id", "plant_id", "machine_type", "status"])
    df = validate_not_null(df, "machines", "machine_id")
    df = validate_unique(df, "machines", "machine_id")
    df = validate_accepted_values(df, "machines", "status", ["ACTIVE", "MAINTENANCE", "IDLE"])
    return df

def validate_raw_materials_table(df):
    df = validate_schema(df, "raw_materials", ["material_id", "supplier_id", "material_name", "unit_of_measure"])
    df = validate_not_null(df, "raw_materials", "material_id")
    df = validate_unique(df, "raw_materials", "material_id")
    return df

def validate_products_table(df):
    df = validate_schema(df, "products", ["product_id", "category_id", "product_name", "standard_cost"])
    df = validate_not_null(df, "products", "product_id")
    df = validate_unique(df, "products", "product_id")
    df = validate_positive_values(df, "products", "standard_cost")
    return df

def validate_production_orders_table(df):
    df = validate_schema(df, "production_orders", ["order_id", "plant_id", "status", "planned_start_date", "actual_start_date"])
    df = validate_not_null(df, "production_orders", "order_id")
    df = validate_unique(df, "production_orders", "order_id")
    df = validate_accepted_values(df, "production_orders", "status", ["PENDING", "IN_PROGRESS", "COMPLETED", "CANCELLED", "PLANNED"])
    return df

def validate_production_yields_table(df):
    df = validate_schema(df, "production_yields", ["yield_id", "order_id", "machine_id", "product_id", "good_quantity", "scrap_quantity", "execution_date"])
    df = validate_not_null(df, "production_yields", "yield_id")
    df = validate_unique(df, "production_yields", "yield_id")
    df = validate_positive_values(df, "production_yields", "good_quantity")
    df = validate_positive_values(df, "production_yields", "scrap_quantity")
    return df

def validate_downtime_events_table(df):
    df = validate_schema(df, "downtime_events", ["event_id", "machine_id", "start_timestamp", "end_timestamp", "reason"])
    df = validate_not_null(df, "downtime_events", "event_id")
    df = validate_unique(df, "downtime_events", "event_id")
    df = validate_chronological_order(df, "downtime_events", "start_timestamp", "end_timestamp")
    return df

def validate_quality_control_table(df):
    df = validate_schema(df, "quality_control", ["quality_id", "production_yield_id", "inspector_name", "quality_score", "is_approved"])
    df = validate_not_null(df, "quality_control", "quality_id")
    df = validate_unique(df, "quality_control", "quality_id")
    df = validate_positive_values(df, "quality_control", "quality_score")
    return df

VALIDATION_RULES = {
    "plants": validate_plants_table,
    "product_categories": validate_product_categories_table,
    "suppliers": validate_suppliers_table,
    "machines": validate_machines_table,
    "raw_materials": validate_raw_materials_table,
    "products": validate_products_table,
    "production_orders": validate_production_orders_table,
    "production_yields": validate_production_yields_table,
    "downtime_events": validate_downtime_events_table,
    "quality_control": validate_quality_control_table
}

# Flujo de Procesamiento Silver

def clean_data(df, table_name):
    """Normaliza columnas y aplica las reglas de limpieza de la tabla."""

    logger.info("Iniciando limpieza de datos para la tabla: %s", table_name)
    
    df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")
    
    if table_name in CLEANING_RULES:
        logger.info("Aplicando reglas de limpieza específicas para la tabla '%s'", table_name)
        df = CLEANING_RULES[table_name](df)
    else:
        logger.info("La tabla '%s' no requiere reglas de limpieza adicionales.", table_name)
        
    df["ingested_at"] = datetime.now(timezone.utc)
    
    logger.info("Limpieza finalizada. Columnas resultantes: %s", list(df.columns))
    return df

# Las validaciones siguen un enfoque fail-fast:
# un incumplimiento impide cargar la tabla en Silver.

def validate_data(df, table_name):
    """Ejecuta las validaciones de calidad definidas para la tabla."""

    logger.info("Iniciando calidad de datos para: %s", table_name)
    
    df = validate_non_empty(df, table_name)

    if table_name in VALIDATION_RULES:
        logger.info("Aplicando reglas de calidad estrictas para '%s'", table_name)
        df = VALIDATION_RULES[table_name](df)
    else:
        logger.info("La tabla '%s' solo requiere validación básica (non_empty).", table_name)
        
    logger.info("Calidad de datos superada con éxito para '%s'", table_name)
    return df

def save_parquet(df, output_dir, filename):
    """Guarda el DataFrame procesado en formato Parquet."""

    output_dir.mkdir(parents=True, exist_ok=True)
    parquet_path = output_dir / filename
    
    logger.info("Guardando archivo Parquet optimizado en: %s", parquet_path)
    df.to_parquet(parquet_path, index=False, engine="pyarrow", coerce_timestamps="us", allow_truncated_timestamps=True)
    
    return parquet_path

def run(table_name, bronze_path, silver_path, ingestion_date):
    """Procesa una tabla desde Bronze hasta Silver y respalda el resultado en GCS."""

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
        df_validated = validate_data(df_clean, table_name)
        
        parquet_path = save_parquet(df_validated, output_dir, filename)
        
        logger.info("Subiendo Data a Cloud Storage (Bucket Silver)")
        
        if not upload_file(parquet_path, GCS_BUCKET_SILVER, f"{cloud_folder}/{parquet_path.name}"):
            raise RuntimeError("Fallo crítico: GCS Uploader retornó False. No se pudo subir el Parquet.")
        
        logger.info("Transformación y respaldo en nube finalizados exitosamente para: '%s'\n", table_name)
        
    except Exception as error:
        logger.error("Error crítico transformando la tabla '%s': %s", table_name, error, exc_info=True)
        raise