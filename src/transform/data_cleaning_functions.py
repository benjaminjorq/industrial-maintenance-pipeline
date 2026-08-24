import logging
import pandas as pd
import numpy as np

logger = logging.getLogger(__name__)

def clean_spaces(df, column_name):
    """Quita espacios en los extremos y colapsa los dobles espacios internos."""
    if column_name in df.columns:
        logger.info("Limpiando espacios en la columna: %s", column_name)
        df[column_name] = df[column_name].astype(str).str.strip().str.replace(r'\s+', ' ', regex=True)
        
    return df

def convert_to_uppercase(df, column_name):
    """Convierte el texto de una columna a letras mayúsculas."""
    if column_name in df.columns:
        logger.info("Convirtiendo a mayúsculas la columna: %s", column_name)
        df[column_name] = df[column_name].astype(str).str.upper()
        
    return df

def convert_to_lowercase(df, column_name):
    """Convierte el texto de una columna a letras minúsculas."""
    if column_name in df.columns:
        logger.info("Convirtiendo a minúsculas la columna: %s", column_name)
        df[column_name] = df[column_name].astype(str).str.lower()
        
    return df

def convert_to_title_case(df, column_name):
    """Convierte el texto para que cada palabra inicie con mayúscula."""
    if column_name in df.columns:
        logger.info("Convirtiendo a formato título la columna: %s", column_name)
        df[column_name] = df[column_name].astype(str).str.title()
        
    return df

def fix_negative_numbers(df, column_name):
    """Convierte los números a valores absolutos para evitar cifras negativas inválidas."""
    if column_name in df.columns:
        logger.info("Corrigiendo números negativos en la columna: %s", column_name)
        df[column_name] = pd.to_numeric(df[column_name], errors='coerce').abs()
        
    return df

def invalidate_zero_costs(df, column_name):
    """Reemplaza los valores iguales a cero por un valor nulo nativo de Pandas."""
    if column_name in df.columns:
        logger.info("Invalidando valores en cero para la columna: %s", column_name)
        df.loc[df[column_name] == 0.0, column_name] = None
        
    return df

def fix_inverted_dates(df, start_col, end_col):
    """Corrige registros donde la fecha de inicio es posterior a la fecha de término."""
    if start_col in df.columns and end_col in df.columns:
        logger.info("Verificando consistencia de fechas entre: %s y %s", start_col, end_col)
        df[start_col] = pd.to_datetime(df[start_col], errors='coerce').astype('datetime64[us]')
        df[end_col] = pd.to_datetime(df[end_col], errors='coerce').astype('datetime64[us]')
        
        invalid_dates = df[start_col] > df[end_col]
        df.loc[invalid_dates, [start_col, end_col]] = df.loc[invalid_dates, [end_col, start_col]].values
        
    return df

def set_missing_dates_to_null(df, column_name):
    """Convierte la columna a datetime, forzando valores inválidos o vacíos a NaT."""
    if column_name in df.columns:
        logger.info("Forzando fechas vacías/nulas a NaT explícito en la columna: %s", column_name)
        df[column_name] = pd.to_datetime(df[column_name], errors='coerce').astype('datetime64[us]')
        
    return df