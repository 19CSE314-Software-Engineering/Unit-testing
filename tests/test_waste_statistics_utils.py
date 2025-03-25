# tests/test_waste_statistics.py
from unittest.mock import MagicMock
import pytest
from tests.test_utils import fetch_waste_levels, parse_waste_level, fetch_assigned_waste_facility_stats

# Fixture to create a mock Supabase client
@pytest.fixture
def mock_supabase():
    supabase = MagicMock()
    supabase.table.return_value.select.return_value.execute.return_value = MagicMock(data=[])
    supabase.table.return_value.select.return_value.eq.return_value.execute.return_value = MagicMock(data=[])
    return supabase

# Tests for fetch_waste_levels
def test_fetch_waste_levels_found(mock_supabase):
    mock_data = [
        {"state_name": "California", "waste_level": "50%"},
        {"state_name": "Texas", "waste_level": 75}
    ]
    mock_supabase.table.return_value.select.return_value.execute.return_value = MagicMock(data=mock_data)
    data = fetch_waste_levels(mock_supabase)
    assert data == mock_data
    mock_supabase.table.assert_called_once_with("waste_facilities")
    mock_supabase.table.return_value.select.assert_called_once_with("state_name, waste_level")

def test_fetch_waste_levels_not_found(mock_supabase):
    mock_supabase.table.return_value.select.return_value.execute.return_value = MagicMock(data=[])
    data = fetch_waste_levels(mock_supabase)
    assert data == []
    mock_supabase.table.assert_called_once_with("waste_facilities")

# Tests for parse_waste_level
def test_parse_waste_level_percentage_string():
    value = parse_waste_level("50%")
    assert value == 50.0

def test_parse_waste_level_numeric():
    value = parse_waste_level(75)
    assert value == 75.0

def test_parse_waste_level_float():
    value = parse_waste_level(75.5)
    assert value == 75.5

def test_parse_waste_level_invalid():
    value = parse_waste_level("invalid")
    assert value is None

# Tests for fetch_assigned_waste_facility_stats
def test_fetch_assigned_waste_facility_stats_found(mock_supabase):
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
    data = fetch_assigned_waste_facility_stats(mock_supabase, employee_id=1)
    assert data == mock_data
    mock_supabase.table.assert_called_once_with("waste_facilities")
    mock_supabase.table.return_value.select.return_value.eq.assert_called_once_with("in_charge_id", 1)

def test_fetch_assigned_waste_facility_stats_not_found(mock_supabase):
    mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value = MagicMock(data=[])
    data = fetch_assigned_waste_facility_stats(mock_supabase, employee_id=1)
    assert data == []
    mock_supabase.table.assert_called_once_with("waste_facilities")