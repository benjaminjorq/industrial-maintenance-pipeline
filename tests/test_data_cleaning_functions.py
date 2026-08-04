import pandas as pd
import numpy as np
from src.transform.data_cleaning_functions import (clean_spaces, convert_to_title_case, convert_to_uppercase,
convert_to_lowercase, fix_negative_numbers, invalidate_zero_costs, set_missing_dates_to_null,fix_inverted_dates)

def test_clean_spaces_region(plants_dirty_df):
    """Valida la eliminación de espacios laterales en regiones."""
    # Arrange
    df = plants_dirty_df.copy()
    
    # Act
    result = clean_spaces(df, "region")
    
    # Assert
    assert result.loc[0, "region"] == "Nuevo Leon"
    assert result.loc[1, "region"] == "colombia"

def test_clean_spaces_plant_name(plants_dirty_df):
    """Valida la eliminación de dobles espacios internos."""
    # Arrange
    df = plants_dirty_df.copy()
    
    # Act
    result = clean_spaces(df, "plant_name")
    
    # Assert
    assert result.loc[2, "plant_name"] == "Planta Berlin"

def test_convert_to_title_case(plants_dirty_df):
    """Valida la capitalización correcta tipo Título, sin alterar espacios."""
    # Arrange
    df = plants_dirty_df.copy()
    
    # Act
    result = convert_to_title_case(df, "region")
    
    # Assert
    assert result.loc[1, "region"] == "Colombia"
    assert result.loc[2, "region"] == "Berlin"

def test_convert_to_uppercase(machines_dirty_df):
    """Valida la conversión estricta a mayúsculas."""
    # Arrange
    df = machines_dirty_df.copy()
    
    # Act
    result = convert_to_uppercase(df, "status")
    
    # Assert
    assert result.loc[0, "status"] == "IDLE"
    assert result.loc[2, "status"] == "ACTIVE" # Era 'active'

def test_convert_to_lowercase(raw_materials_dirty_df):
    """Valida la conversión estricta a minúsculas para unidades, sin alterar espacios."""
    # Arrange
    df = raw_materials_dirty_df.copy()
    
    # Act
    result = convert_to_lowercase(df, "unit_of_measure")
    
    # Assert
    assert result.loc[0, "unit_of_measure"] == "kg" # Era 'KG'
    assert result.loc[1, "unit_of_measure"] == "l  " # Era 'L  '

def test_fix_negative_numbers(products_dirty_df):
    """Valida la corrección de valores numéricos incongruentes (negativos)."""
    # Arrange
    df = products_dirty_df.copy()
    
    # Act
    result = fix_negative_numbers(df, "standard_cost")
    
    # Assert
    assert result.loc[1, "standard_cost"] == 15.5 # Era -15.5

def test_invalidate_zero_costs(products_dirty_df):
    """Valida que los valores en cero sean interpretados como nulos (NaN)."""
    # Arrange
    df = products_dirty_df.copy()
    
    # Act
    result = invalidate_zero_costs(df, "standard_cost")
    
    # Assert
    assert pd.isna(result.loc[2, "standard_cost"]) # Era 0.0

def test_set_missing_dates_to_null(production_orders_dirty_df):
    """Valida el manejo de fechas nulas (None o np.nan) a formato nativo."""
    # Arrange
    df = production_orders_dirty_df.copy()
    
    # Act
    result = set_missing_dates_to_null(df, "actual_start_date")
    
    # Assert
    assert pd.notna(result.loc[0, "actual_start_date"])
    assert pd.isna(result.loc[1, "actual_start_date"])
    assert pd.isna(result.loc[2, "actual_start_date"])

def test_fix_inverted_dates(downtime_events_dirty_df):
    """Valida la corrección de fechas invertidas."""
    # Arrange
    df = downtime_events_dirty_df.copy()
    
    # Act
    result = fix_inverted_dates(df, "start_timestamp", "end_timestamp")
    
    # Assert (El evento 4, índice 1, estaba invertido)
    assert result.loc[1, "start_timestamp"] == pd.to_datetime("2026-07-01 06:30:00")
    assert result.loc[1, "end_timestamp"] == pd.to_datetime("2026-07-01 07:16:00")