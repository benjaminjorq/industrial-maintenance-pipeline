import pytest
import pandas as pd
import numpy as np

@pytest.fixture
def plants_dirty_df():
    """Esquema y muestra real de la tabla plants."""
    return pd.DataFrame({
        "plant_id": [1, 2, 7],
        "plant_name": ["Planta Monterrey", "Planta Bogota", "Planta  Berlin"],
        "region": ["  Nuevo Leon ", "colombia", "berlin"],
        "is_active": [True, True, True]
    })

@pytest.fixture
def product_categories_dirty_df():
    """Esquema y muestra real de la tabla product_categories."""
    return pd.DataFrame({
        "category_id": [1, 2, 3],
        "category_name": ["Empaques Flexibles", "  Componentes Electronicos", "piezas metalicas"]
    })

@pytest.fixture
def suppliers_dirty_df():
    """Esquema y muestra real de la tabla suppliers."""
    return pd.DataFrame({
        "supplier_id": [1, 2, 6],
        "supplier_name": ["Acero del Norte S.A.", "Global Polymers Inc", " Envases Continental"],
        "country": ["Mexico", "  Estados Unidos", "Brasil"]
    })

@pytest.fixture
def machines_dirty_df():
    """Esquema y muestra real de la tabla machines."""
    return pd.DataFrame({
        "machine_id": [1, 2, 7],
        "plant_id": [2, 4, 7],
        "machine_type": ["Extrusora", "Ensambladora", "Ensambladora"],
        "status": ["IDLE", "MAINTENANCE", "active"]
    })

@pytest.fixture
def raw_materials_dirty_df():
    """Esquema y muestra real de la tabla raw_materials."""
    return pd.DataFrame({
        "material_id": [1, 4, 7],
        "supplier_id": [6, 3, 2],
        "material_name": ["Resina PET", "Pigmento Azul", "Granulado Plastico"],
        "unit_of_measure": ["KG", "L  ", "kg"]
    })

@pytest.fixture
def products_dirty_df():
    """Esquema y muestra real de la tabla products."""
    return pd.DataFrame({
        "product_id": [1, 3, 8],
        "category_id": [1, 3, 5],
        "product_name": ["Bolsa Laminada 500g", "Bisagra Reforzada", "Placa de Acero 3mm"],
        "standard_cost": [13.4, -15.5, 0.0]
    })

@pytest.fixture
def production_orders_dirty_df():
    """Esquema y muestra real de la tabla production_orders."""
    return pd.DataFrame({
        "order_id": [1, 3, 4],
        "plant_id": [8, 2, 5],
        "status": ["COMPLETED", "CANCELLED", "completed"],
        "planned_start_date": ["2026-07-01", "2026-07-01", "2026-07-01"],
        "actual_start_date": ["2026-07-01", None, np.nan]
    })

@pytest.fixture
def production_yields_dirty_df():
    """Esquema y muestra real de la tabla production_yields."""
    return pd.DataFrame({
        "yield_id": [1, 2, 3],
        "order_id": [7, 12, 3],
        "machine_id": [9, 8, 6],
        "product_id": [4, 9, 1],
        "good_quantity": [415, 281, 351],
        "scrap_quantity": [21, -8, 18],
        "execution_date": ["2026-07-01", "2026-07-01", "2026-07-01"]
    })

@pytest.fixture
def downtime_events_dirty_df():
    """Esquema y muestra real de la tabla downtime_events (incluyendo eventos invertidos 4 y 5)."""
    return pd.DataFrame({
        "event_id": [1, 4, 5],
        "machine_id": [2, 6, 8],
        "start_timestamp": ["2026-07-01 07:25:00", "2026-07-01 07:16:00", "2026-07-01 10:59:00"],
        "end_timestamp": ["2026-07-01 08:05:00", "2026-07-01 06:30:00", "2026-07-01 10:15:00"],
        "reason": ["Corte electrico", "Mantenimiento preventivo", "Corte electrico"]
    })