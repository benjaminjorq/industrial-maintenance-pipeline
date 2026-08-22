import logging
import pandas as pd
import numpy as np

logger = logging.getLogger(__name__)

# Instrucciones de mantenimiento:
# Si el negocio requiere una nueva operación de limpieza (ej. extraer números de un texto),
# crea una nueva función aquí. Toda función debe recibir el DataFrame y el nombre de la columna,
# verificar que la columna exista, procesarla y retornar el DataFrame modificado.

def clean_spaces(df: pd.DataFrame, column_name: str) -> pd.DataFrame:
    """Quita espacios en los extremos y colapsa los dobles espacios internos."""
    if column_name in df.columns:
        logger.info("Limpiando espacios en la columna: %s", column_name)
        df[column_name] = df[column_name].astype(str).str.strip().str.replace(r'\s+', ' ', regex=True)
        
    return df

def convert_to_uppercase(df: pd.DataFrame, column_name: str) -> pd.DataFrame:
    """Convierte el texto de una columna a letras mayúsculas."""
    if column_name in df.columns:
        logger.info("Convirtiendo a mayúsculas la columna: %s", column_name)
        df[column_name] = df[column_name].astype(str).str.upper()
        
    return df

def convert_to_lowercase(df: pd.DataFrame, column_name: str) -> pd.DataFrame:
    """Convierte el texto de una columna a letras minúsculas."""
    if column_name in df.columns:
        logger.info("Convirtiendo a minúsculas la columna: %s", column_name)
        df[column_name] = df[column_name].astype(str).str.lower()
        
    return df

def convert_to_title_case(df: pd.DataFrame, column_name: str) -> pd.DataFrame:
    """Convierte el texto para que cada palabra inicie con mayúscula."""
    if column_name in df.columns:
        logger.info("Convirtiendo a formato título la columna: %s", column_name)
        df[column_name] = df[column_name].astype(str).str.title()
        
    return df

def fix_negative_numbers(df: pd.DataFrame, column_name: str) -> pd.DataFrame:
    """Convierte los números a valores absolutos para evitar cifras negativas inválidas."""
    if column_name in df.columns:
        logger.info("Corrigiendo números negativos en la columna: %s", column_name)
        df[column_name] = pd.to_numeric(df[column_name], errors='coerce').abs()
        
    return df

def invalidate_zero_costs(df: pd.DataFrame, column_name: str) -> pd.DataFrame:
    """Reemplaza los valores iguales a cero por un valor nulo nativo de Pandas."""
    if column_name in df.columns:
        logger.info("Invalidando valores en cero para la columna: %s", column_name)
        df.loc[df[column_name] == 0.0, column_name] = None
        
    return df

def fix_inverted_dates(df: pd.DataFrame, start_col: str, end_col: str) -> pd.DataFrame:
    """Intercambia fechas de inicio y fin si el orden cronológico es incorrecto.

    Corrige inconsistencias comunes generadas por errores humanos al ingresar 
    registros manuales (como mantenimientos o turnos) en los orígenes de datos.

    Args:
        df: DataFrame a procesar.
        start_col: Nombre de la columna con la fecha de inicio.
        end_col: Nombre de la columna con la fecha de término.

    Returns:
        DataFrame con las fechas ordenadas lógicamente.
    """
    if start_col in df.columns and end_col in df.columns:
        logger.info("Verificando consistencia de fechas entre: %s y %s", start_col, end_col)
        df[start_col] = pd.to_datetime(df[start_col], errors='coerce').astype('datetime64[us]')
        df[end_col] = pd.to_datetime(df[end_col], errors='coerce').astype('datetime64[us]')
        
        invalid_dates = df[start_col] > df[end_col]
        df.loc[invalid_dates, [start_col, end_col]] = df.loc[invalid_dates, [end_col, start_col]].values
        
    return df

def set_missing_dates_to_null(df: pd.DataFrame, column_name: str) -> pd.DataFrame:
    """Convierte la columna a datetime, forzando valores inválidos o vacíos a NaT.

    Garantiza que fechas inexistentes (ej. órdenes no iniciadas) lleguen al 
    Data Warehouse como verdaderos NULL, evitando fechas falsas por defecto.

    Args:
        df: DataFrame a procesar.
        column_name: Nombre de la columna.

    Returns:
        DataFrame con las fechas estandarizadas.
    """
    if column_name in df.columns:
        logger.info("Forzando fechas vacías/nulas a NaT explícito en la columna: %s", column_name)
        df[column_name] = pd.to_datetime(df[column_name], errors='coerce').astype('datetime64[us]')
        
    return df