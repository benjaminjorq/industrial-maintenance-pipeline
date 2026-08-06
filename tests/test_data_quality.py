import pandas as pd
import pytest

from src.validations.data_quality import (
    validate_non_empty,
    validate_schema,
    validate_not_null,
    validate_unique,
    validate_accepted_values,
    validate_positive_values,
    validate_chronological_order,
)


@pytest.fixture
def valid_df():
    return pd.DataFrame({
        "id": [1, 2, 3],
        "status": ["ACTIVE", "MAINTENANCE", "ACTIVE"],
        "cost": [100.0, 200.0, 300.0],
        "start_date": pd.to_datetime(["2026-07-01", "2026-07-02", "2026-07-03"]),
        "end_date": pd.to_datetime(["2026-07-10", "2026-07-11", "2026-07-12"])
    })


# validate_non_empty

def test_validate_non_empty_success(valid_df):
    result = validate_non_empty(valid_df, "test_table")
    assert len(result) == 3

def test_validate_non_empty_fails():
    with pytest.raises(ValueError, match=r"Dataset vacío"):
        validate_non_empty(pd.DataFrame(), "test_table")


# validate_schema

def test_validate_schema_success(valid_df):
    result = validate_schema(valid_df, "test_table", ["id", "status", "cost"])
    assert result.equals(valid_df)

def test_validate_schema_fails(valid_df):
    with pytest.raises(ValueError, match=r"Faltan \d+ columnas"):
        validate_schema(valid_df, "test_table", ["id", "status", "cost", "fake_column"])


# validate_not_null

def test_validate_not_null_success(valid_df):
    result = validate_not_null(valid_df, "test_table", "status")
    assert result.equals(valid_df)

def test_validate_not_null_fails():
    df = pd.DataFrame({"status": ["ACTIVE", None]})
    with pytest.raises(ValueError, match=r"\d+ valores nulos"):
        validate_not_null(df, "test_table", "status")


# validate_unique

def test_validate_unique_success(valid_df):
    result = validate_unique(valid_df, "test_table", "id")
    assert result.equals(valid_df)

def test_validate_unique_fails():
    df = pd.DataFrame({"id": [1, 1, 2]})
    with pytest.raises(ValueError, match=r"\d+ valores duplicados"):
        validate_unique(df, "test_table", "id")


# validate_accepted_values

def test_validate_accepted_values_success(valid_df):
    allowed = ["ACTIVE", "MAINTENANCE"]
    result = validate_accepted_values(valid_df, "test_table", "status", allowed)
    assert result.equals(valid_df)

def test_validate_accepted_values_fails():
    df = pd.DataFrame({"status": ["ACTIVE", "BROKEN"]})
    with pytest.raises(ValueError, match=r"\d+ valores inválidos"):
        validate_accepted_values(df, "test_table", "status", ["ACTIVE", "MAINTENANCE"])


# validate_positive_values

def test_validate_positive_values_success(valid_df):
    result = validate_positive_values(valid_df, "test_table", "cost")
    assert result.equals(valid_df)

def test_validate_positive_values_fails():
    df = pd.DataFrame({"cost": [100.0, -20.0]})
    with pytest.raises(ValueError, match=r"\d+ valores negativos"):
        validate_positive_values(df, "test_table", "cost")


# validate_chronological_order

def test_validate_chronological_order_success(valid_df):
    result = validate_chronological_order(valid_df, "test_table", "start_date", "end_date")
    assert result.equals(valid_df)

def test_validate_chronological_order_fails():
    df = pd.DataFrame({
        "start_date": pd.to_datetime(["2026-07-10"]),
        "end_date": pd.to_datetime(["2026-07-01"])
    })
    with pytest.raises(ValueError, match=r"\d+ registros con fechas invertidas"):
        validate_chronological_order(df, "test_table", "start_date", "end_date")