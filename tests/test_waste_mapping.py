# tests/test_waste_mapping.py
from unittest.mock import MagicMock
import pytest
from tests.test_utils import fetch_waste_facility_data, get_waste_level_color, count_waste_levels, fetch_assigned_waste_facility_map

# Fixture to create a mock Supabase client
@pytest.fixture
def mock_supabase():
    supabase = MagicMock()
    supabase.table.return_value.select.return_value.execute.return_value = MagicMock(data=[])
    supabase.table.return_value.select.return_value.eq.return_value.execute.return_value = MagicMock(data=[])
    return supabase

# Tests for fetch_waste_facility_data
def test_fetch_waste_facility_data_found(mock_supabase):
    mock_data = [
        {
            "facility_id": 1,
            "state_name": "California",
            "latitude": 34.0,
            "longitude": -118.0,
            "waste_level": 500,
            "capacity": 1000,
            "employees": {"name": "John Doe", "id": 1}
        }
    ]
    mock_supabase.table.return_value.select.return_value.execute.return_value = MagicMock(data=mock_data)
    data = fetch_waste_facility_data(mock_supabase)
    assert data == mock_data
    mock_supabase.table.assert_called_once_with("waste_facilities")
    mock_supabase.table.return_value.select.assert_called_once_with("*, employees(name, id)")

def test_fetch_waste_facility_data_not_found(mock_supabase):
    mock_supabase.table.return_value.select.return_value.execute.return_value = MagicMock(data=[])
    data = fetch_waste_facility_data(mock_supabase)
    assert data == []
    mock_supabase.table.assert_called_once_with("waste_facilities")

# Tests for get_waste_level_color
def test_get_waste_level_color_low():
    color = get_waste_level_color(waste_level=200, total_capacity=1000)
    assert color == "green"  # 20% < 30%

def test_get_waste_level_color_medium():
    color = get_waste_level_color(waste_level=500, total_capacity=1000)
    assert color == "yellow"  # 50% between 30% and 70%

def test_get_waste_level_color_high():
    color = get_waste_level_color(waste_level=800, total_capacity=1000)
    assert color == "red"  # 80% > 70%

def test_get_waste_level_color_invalid():
    color = get_waste_level_color(waste_level=None, total_capacity=1000)
    assert color == "gray"

# Tests for count_waste_levels
def test_count_waste_levels():
    waste_data = [
        {"waste_level": 200, "capacity": 1000},  # 20% (Low)
        {"waste_level": 500, "capacity": 1000},  # 50% (Medium)
        {"waste_level": 800, "capacity": 1000},  # 80% (High)
        {"waste_level": None, "capacity": 1000}  # Invalid, should be skipped
    ]
    counts = count_waste_levels(waste_data)
    assert counts == {
        "Low (<30%)": 1,
        "Medium (30%-70%)": 1,
        "High (>70%)": 1
    }

def test_count_waste_levels_empty():
    counts = count_waste_levels([])
    assert counts == {
        "Low (<30%)": 0,
        "Medium (30%-70%)": 0,
        "High (>70%)": 0
    }

# Tests for fetch_assigned_waste_facility_map
def test_fetch_assigned_waste_facility_map_found(mock_supabase):
    mock_data = [
        {
            "facility_id": 1,
            "state_name": "California",
            "status": "Active",
            "description": "Main landfill",
            "last_updated": "2023-01-01",
            "capacity": 1000,
            "waste_level": 50
        }
    ]
    mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value = MagicMock(data=mock_data)
    data = fetch_assigned_waste_facility_map(mock_supabase, employee_id=1)
    assert data == mock_data
    mock_supabase.table.assert_called_once_with("waste_facilities")
    mock_supabase.table.return_value.select.return_value.eq.assert_called_once_with("in_charge_id", 1)

def test_fetch_assigned_waste_facility_map_not_found(mock_supabase):
    mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value = MagicMock(data=[])
    data = fetch_assigned_waste_facility_map(mock_supabase, employee_id=1)
    assert data == []
    mock_supabase.table.assert_called_once_with("waste_facilities")