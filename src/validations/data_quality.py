import logging
import pandas as pd

logger = logging.getLogger(__name__)

def validate_non_empty(df, table_name):
    """Verifica que el DataFrame contenga al menos un registro."""

    logger.info("Validando que la tabla '%s' no esté vacía", table_name)
    
    if df.empty:
        logger.error("Error crítico: La tabla '%s' está vacía", table_name)
        raise ValueError(f"Data Quality: Dataset vacío en '{table_name}'")
        
    return df

def validate_schema(df, table_name, expected_cols):
    """Verifica que el DataFrame tenga todas las columnas obligatorias."""

    logger.info("Validando esquema (schema) en '%s'", table_name)
    
    missing_cols = [col for col in expected_cols if col not in df.columns]
    
    if missing_cols:
        logger.error("Error crítico: Faltan %s columnas en '%s': %s", len(missing_cols), table_name, missing_cols)
        raise ValueError(f"Data Quality: Faltan {len(missing_cols)} columnas {missing_cols} en '{table_name}'")
        
    return df

def validate_not_null(df, table_name, column_name):
    """Asegura que una columna exista y no contenga valores nulos."""

    if column_name not in df.columns:
        logger.error("Error crítico: La columna '%s' no existe en '%s'", column_name, table_name)
        raise ValueError(f"Data Quality: Columna '{column_name}' no existe en '{table_name}'")
        
    logger.info("Validando ausencia de nulos en '%s.%s'", table_name, column_name)
    
    null_count = df[column_name].isnull().sum()
    
    if null_count > 0:
        logger.error("Error crítico: Se encontraron %s valores nulos en '%s.%s'", null_count, table_name, column_name)
        raise ValueError(f"Data Quality: Se encontraron {null_count} valores nulos en '{table_name}.{column_name}'")
        
    return df

def validate_unique(df, table_name, column_name):
    """Valida que una columna no contenga valores duplicados."""

    if column_name not in df.columns:
        logger.error("Error crítico: La columna '%s' no existe en '%s'", column_name, table_name)
        raise ValueError(f"Data Quality: Columna '{column_name}' no existe en '{table_name}'")
        
    logger.info("Validando valores únicos (unique) en '%s.%s'", table_name, column_name)
    
    duplicate_count = df[column_name].duplicated().sum()
    
    if duplicate_count > 0:
        logger.error("Error crítico: Se encontraron %s valores duplicados en '%s.%s'", duplicate_count, table_name, column_name)
        raise ValueError(f"Data Quality: Se encontraron {duplicate_count} valores duplicados en '{table_name}.{column_name}'")
        
    return df

def validate_accepted_values(df, table_name, column_name, allowed_values):
    """Asegura que los datos de una columna estén dentro de una lista permitida."""

    if column_name not in df.columns:
        logger.error("Error crítico: La columna '%s' no existe en '%s'", column_name, table_name)
        raise ValueError(f"Data Quality: Columna '{column_name}' no existe en '{table_name}'")
        
    logger.info("Validando valores aceptados (accepted_values) en '%s.%s'", table_name, column_name)
    
    invalid_data = df[~df[column_name].isin(allowed_values)]
    invalid_count = len(invalid_data)
    
    if invalid_count > 0:
        invalid_vals = invalid_data[column_name].unique().tolist()
        logger.error("Error crítico: Se encontraron %s valores inválidos %s en '%s.%s'", invalid_count, invalid_vals, table_name, column_name)
        raise ValueError(f"Data Quality: Se encontraron {invalid_count} valores inválidos {invalid_vals} en '{table_name}.{column_name}'")
        
    return df

def validate_positive_values(df, table_name, column_name):
    """Verifica que una métrica numérica no contenga valores negativos."""
    if column_name not in df.columns:
        logger.error("Error crítico: La columna '%s' no existe en '%s'", column_name, table_name)
        raise ValueError(f"Data Quality: Columna '{column_name}' no existe en '{table_name}'")
        
    logger.info("Validando métricas positivas (positive_values) en '%s.%s'", table_name, column_name)
    
    numeric_col = pd.to_numeric(df[column_name], errors='coerce')
    negative_count = (numeric_col < 0).sum()
    
    if negative_count > 0:
        logger.error("Error crítico: Se encontraron %s valores negativos en '%s.%s'", negative_count, table_name, column_name)
        raise ValueError(f"Data Quality: Se encontraron {negative_count} valores negativos en '{table_name}.{column_name}'")
        
    return df

def validate_chronological_order(df, table_name, start_col, end_col):
    """Verifica que la fecha de inicio no sea mayor a la de fin."""
    
    if start_col not in df.columns:
        logger.error("Error crítico: La columna '%s' no existe en '%s'", start_col, table_name)
        raise ValueError(f"Data Quality: Columna '{start_col}' no existe en '{table_name}'")
        
    if end_col not in df.columns:
        logger.error("Error crítico: La columna '%s' no existe en '%s'", end_col, table_name)
        raise ValueError(f"Data Quality: Columna '{end_col}' no existe en '{table_name}'")
        
    logger.info("Validando orden cronológico entre '%s' y '%s' en '%s'", start_col, end_col, table_name)
    
    start_dates = pd.to_datetime(df[start_col], errors='coerce')
    end_dates = pd.to_datetime(df[end_col], errors='coerce')
    
    invalid_dates = (start_dates > end_dates).sum()
    
    if invalid_dates > 0:
        logger.error("Error crítico: Se encontraron %s registros con fechas invertidas en '%s'", invalid_dates, table_name)
        raise ValueError(f"Data Quality: Se encontraron {invalid_dates} registros con fechas invertidas en '{table_name}'")
        
    return df