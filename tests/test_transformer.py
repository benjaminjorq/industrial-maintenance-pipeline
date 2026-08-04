import pandas as pd
from pathlib import Path
from src.transform.transformer import (clean_plants_table,clean_raw_materials_table,clean_products_table,
clean_production_orders_table, clean_downtime_events_table)

def test_clean_plants_table(plants_dirty_df):
    """Valida limpieza de texto y espacios en tabla Plants."""
    # Arrange
    df = plants_dirty_df.copy()
    
    # Act
    result = clean_plants_table(df)
    
    # Assert
    assert result.loc[2, "plant_name"] == "Planta Berlin"
    assert result.loc[0, "region"] == "Nuevo Leon"
    assert result.loc[1, "region"] == "Colombia"

def test_clean_raw_materials_table(raw_materials_dirty_df):
    """Valida limpieza y formato minúscula en tabla Materiales."""
    # Arrange
    df = raw_materials_dirty_df.copy()
    
    # Act
    result = clean_raw_materials_table(df)
    
    # Assert
    assert result.loc[0, "unit_of_measure"] == "kg"
    assert result.loc[1, "unit_of_measure"] == "l"

def test_clean_products_table(products_dirty_df):
    """Valida limpieza de métricas financieras (costos)."""
    # Arrange
    df = products_dirty_df.copy()
    
    # Act
    result = clean_products_table(df)
    
    # Assert
    assert result.loc[1, "standard_cost"] == 15.5

def test_clean_production_orders_table(production_orders_dirty_df):
    """Valida limpieza agrupada de status y parseo de fechas."""
    # Arrange
    df = production_orders_dirty_df.copy()
    
    # Act
    result = clean_production_orders_table(df)

    # Assert
    assert result.loc[2, "status"] == "COMPLETED" 
    assert pd.isna(result.loc[1, "actual_start_date"])

def test_clean_downtime_events_table(downtime_events_dirty_df):
    """Valida la ejecución correcta de las reglas para la tabla downtime."""
    # Arrange
    df = downtime_events_dirty_df.copy()
    
    # Act
    result = clean_downtime_events_table(df)
    
    # Assert (Verificamos evento 5, índice 2)
    assert result.loc[2, "start_timestamp"] == pd.to_datetime("2026-07-01 10:15:00")
    assert result.loc[2, "end_timestamp"] == pd.to_datetime("2026-07-01 10:59:00")